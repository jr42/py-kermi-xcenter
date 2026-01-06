"""Base device class for all Kermi devices (Modbus and HTTP)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from ..exceptions import (
    ConnectionError,
    DataConversionError,
    ReadOnlyRegisterError,
    RegisterReadError,
    ValidationError,
)
from ..registers import RegisterDef
from ..types import UnitId

if TYPE_CHECKING:
    from ..client import KermiModbusClient
    from ..http.client import KermiHttpClient
    from ..http.models import DeviceInfo

logger = logging.getLogger(__name__)


@runtime_checkable
class KermiClientProtocol(Protocol):
    """Protocol defining the interface for Kermi clients.

    Both KermiModbusClient and KermiHttpClient implement this protocol,
    allowing device models to work with either client type.
    """

    async def connect(self) -> None:
        """Connect to the device."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        ...

    async def is_connected(self) -> bool:
        """Check if connected."""
        ...

    async def read_register(self, address: int, unit_id: int, count: int = 1) -> int:
        """Read a register value."""
        ...

    async def write_register(self, address: int, value: int, unit_id: int) -> None:
        """Write a register value."""
        ...

    async def reconnect(self) -> None:
        """Reconnect to the device."""
        ...


class KermiDevice:
    """Base class for Kermi devices (Modbus and HTTP).

    Provides common functionality for reading and writing registers
    with automatic data type conversion and validation.

    Works with both KermiModbusClient and KermiHttpClient, allowing
    the same device model code to be used with either transport.

    Attributes:
        client: Client instance (Modbus or HTTP)
        unit_id: Modbus unit ID for this device
        registers: Dictionary of register definitions for this device
    """

    def __init__(
        self,
        client: KermiModbusClient | KermiHttpClient,
        unit_id: UnitId,
        registers: dict[str, RegisterDef],
        capabilities: dict[str, bool] | None = None,
    ) -> None:
        """Initialize the device.

        Args:
            client: Client instance (KermiModbusClient or KermiHttpClient)
            unit_id: Modbus unit ID
            registers: Register definitions for this device
            capabilities: Optional pre-discovered capabilities dict mapping register
                names to availability (True=available, False=unavailable).
                If provided, unavailable registers will be skipped without attempting
                to read them, improving performance.
        """
        self.client = client
        self.unit_id = unit_id
        self.registers = registers
        self._capabilities: dict[str, bool] = capabilities.copy() if capabilities else {}

    def _is_http_client(self) -> bool:
        """Check if using HTTP client."""
        return hasattr(self.client, "get_all_values")

    async def _read_register(self, register: RegisterDef) -> float | int | bool | None:
        """Read a register and convert to engineering units.

        This method automatically handles unavailable registers by returning None
        instead of raising exceptions. This follows the Pythonic pattern of dict.get()
        and os.getenv() for graceful handling of missing data.

        Connection recovery is automatic - if a malformed Modbus frame corrupts the
        connection, this method will reconnect transparently.

        Args:
            register: Register definition

        Returns:
            Converted value in engineering units (or bool for boolean registers),
            or None if the register is not available on this device.

        Raises:
            RegisterReadError: If read fails for reasons other than unsupported register
            DataConversionError: If conversion to engineering units fails
            ConnectionError: If connection fails and cannot be recovered
        """
        # Check capabilities cache first
        if register.name in self._capabilities and not self._capabilities[register.name]:
            logger.debug(f"Skipping '{register.name}' (cached as unavailable on this device)")
            return None

        try:
            raw_value = await self.client.read_register(
                address=register.address,
                unit_id=self.unit_id,
            )
        except Exception as e:
            # Check if this is a protocol-level error indicating unsupported register
            if self._is_unsupported_register_error(e):
                # Reconnect to recover from connection corruption caused by malformed frame
                try:
                    logger.debug(
                        f"Register '{register.name}' not available on this device. "
                        f"Reconnecting after malformed frame..."
                    )
                    await self.client.reconnect()
                except Exception as reconnect_error:
                    logger.warning(
                        f"Reconnection failed after reading '{register.name}': {reconnect_error}. "
                        f"Continuing with existing connection..."
                    )

                # Cache as unavailable for future calls
                self._capabilities[register.name] = False

                # Return None for unavailable register (Pythonic pattern)
                return None

            # Re-raise other errors as-is (connection errors, etc.)
            raise

        # Handle type conversion
        if isinstance(raw_value, list):
            if not raw_value:
                # Empty response - treat as unsupported
                logger.debug(f"Register '{register.name}' returned empty response")
                return None
            raw_value = raw_value[0]

        # Wrap converter exceptions
        converted_value: float | int | bool
        try:
            if register.data_type == "bool":
                converted_value = bool(raw_value)
            elif register.data_type == "enum":
                converted_value = raw_value
            elif register.converter:
                converted_value = register.converter(raw_value)
            else:
                converted_value = raw_value
        except (TypeError, ValueError, ArithmeticError) as e:
            raise DataConversionError(register.name, raw_value, f"{type(e).__name__}: {e}") from e

        # Validate range for numeric values (filter invalid sensor data)
        if isinstance(converted_value, (int, float)) and not isinstance(converted_value, bool):
            if register.min_valid_value is not None and converted_value < register.min_valid_value:
                logger.warning(
                    f"Register '{register.name}': value {converted_value} {register.unit} "
                    f"below physically valid minimum ({register.min_valid_value} {register.unit}). "
                    f"This likely indicates disconnected/faulty sensor. Returning None."
                )
                return None

            if register.max_valid_value is not None and converted_value > register.max_valid_value:
                logger.warning(
                    f"Register '{register.name}': value {converted_value} {register.unit} "
                    f"above physically valid maximum ({register.max_valid_value} {register.unit}). "
                    f"This likely indicates disconnected/faulty sensor. Returning None."
                )
                return None

        return converted_value

    async def _write_register(self, register: RegisterDef, value: float | int | bool) -> None:
        """Write a value to a register with validation.

        Args:
            register: Register definition
            value: Value in engineering units

        Raises:
            ReadOnlyRegisterError: If register is read-only
            ValidationError: If value is out of range
            RegisterWriteError: If write fails
        """
        # Check if writable
        if not register.is_writable:
            raise ReadOnlyRegisterError(register.name)

        # Validate range
        if register.min_value is not None and value < register.min_value:
            raise ValidationError(
                register.name,
                value,
                f"Value below minimum ({register.min_value})",
            )
        if register.max_value is not None and value > register.max_value:
            raise ValidationError(
                register.name,
                value,
                f"Value above maximum ({register.max_value})",
            )

        # Convert to raw value
        if register.data_type == "bool":
            raw_value = int(bool(value))
        elif register.data_type == "enum":
            raw_value = int(value)
        elif register.inverse_converter:
            raw_value = register.inverse_converter(value)
        else:
            raw_value = int(value)

        # Write to device
        await self.client.write_register(
            address=register.address,
            value=raw_value,
            unit_id=self.unit_id,
        )

        logger.info(
            f"Wrote {value} {register.unit} to {register.name} "
            f"(unit {self.unit_id}, register {register.address}, raw: {raw_value})"
        )

    def _is_unsupported_register_error(self, exception: Exception) -> bool:
        """Check if exception indicates unsupported register.

        Args:
            exception: Exception to check

        Returns:
            True if this indicates register not available on device
        """
        # Check for ModbusIOException (malformed frames) in exception chain
        current: BaseException | None = exception
        while current is not None:
            exception_type = type(current).__name__
            if exception_type == "ModbusIOException":
                return True
            current = current.__cause__

        # Check for specific error patterns in message
        error_msg = str(exception).lower()
        unsupported_patterns = [
            "unable to decode",
            "malformed frame",
            "invalid response",
            "byte_count",
        ]
        return any(pattern in error_msg for pattern in unsupported_patterns)

    async def discover_capabilities(self) -> dict[str, bool]:
        """Discover which registers are available on this device.

        This method probes all readable registers to determine which are available
        on this specific device. Results can be saved and reused to skip unavailable
        registers in future sessions, improving performance.

        The discovery process logs progress and automatically handles connection
        recovery if needed. This may take some time for devices with many registers.

        Returns:
            Dictionary mapping register names to availability (True=available, False=unavailable)

        Example:
            >>> hp = HeatPump(client)
            >>> async with client:
            ...     caps = await hp.discover_capabilities()
            ...     print(f"Discovered {sum(caps.values())}/{len(caps)} available registers")
            ...
            ...     # Create new instance with capabilities for faster operation
            ...     hp = HeatPump(client, capabilities=caps)
        """
        capabilities: dict[str, bool] = {}

        # Count readable registers
        readable_registers = {
            name: register for name, register in self.registers.items() if "R" in register.attribute
        }

        logger.info(
            f"Discovering capabilities for {self.__class__.__name__} (Unit {self.unit_id})..."
        )
        logger.info(f"Probing {len(readable_registers)} readable registers...")

        for name, register in readable_registers.items():
            try:
                # Use _read_register which handles reconnection automatically
                value = await self._read_register(register)
                capabilities[name] = value is not None

                if capabilities[name]:
                    logger.debug(f"  ✅ {name}: available (value: {value})")
                else:
                    logger.debug(f"  ⚠️  {name}: returned None (unavailable or invalid)")

            except Exception as e:
                # Unexpected error during probe
                logger.warning(f"  ⚠️  {name}: probe failed ({type(e).__name__}: {e})")
                capabilities[name] = False

        # Summary
        available_count = sum(1 for v in capabilities.values() if v)
        logger.info(
            f"Discovery complete: {available_count}/{len(capabilities)} registers available"
        )

        return capabilities

    async def get_all_readable_values(self) -> dict[str, Any]:
        """Read all readable registers and return as a dictionary.

        This method is resilient to device variations - unavailable registers
        automatically return None without raising exceptions. Connection recovery
        is handled transparently by the underlying _read_register() method.

        Returns:
            Dictionary mapping register names to values.
            Unavailable or failed registers are set to None.

        Note:
            This method reads each register individually, which may be slow.
            Consider using specific getter methods for production use.
        """
        values: dict[str, Any] = {}
        none_count = 0

        for name, register in self.registers.items():
            if "R" not in register.attribute:
                continue

            try:
                value = await self._read_register(register)
                values[name] = value
                if value is None:
                    none_count += 1

            except DataConversionError as e:
                # Converter failed - data read OK but conversion failed
                logger.warning(
                    f"Failed to convert '{name}' (raw value {e.raw_value}): {e}. "
                    f"This may indicate unexpected firmware behavior."
                )
                values[name] = None
                none_count += 1

            except (RegisterReadError, ConnectionError, ValidationError) as e:
                # Standard errors
                logger.warning(f"Failed to read '{name}': {type(e).__name__}: {e}")
                values[name] = None
                none_count += 1

            except Exception as e:
                # Catch-all for truly unexpected errors
                logger.error(
                    f"Unexpected error reading '{name}': {type(e).__name__}: {e}",
                    exc_info=True,
                )
                values[name] = None
                none_count += 1

        # Summary logging
        total_readable = len([r for r in self.registers.values() if "R" in r.attribute])
        available_count = total_readable - none_count
        if none_count > 0:
            logger.info(
                f"Read {available_count}/{total_readable} registers successfully. "
                f"{none_count} register(s) unavailable on this device."
            )

        return values

    # =========================================================================
    # HTTP-Only Methods
    # =========================================================================

    async def get_all_values(self) -> dict[str, Any]:
        """Get all datapoint values efficiently (HTTP only).

        This method is only available when using KermiHttpClient.
        It fetches all datapoints in 2 API calls, making it much more
        efficient than reading registers individually.

        Returns:
            Dictionary mapping attribute names to values

        Raises:
            AttributeError: If using Modbus client (use get_all_readable_values instead)
        """
        if not self._is_http_client():
            raise AttributeError(
                "get_all_values() is only available with KermiHttpClient. "
                "Use get_all_readable_values() for Modbus."
            )
        return await self.client.get_all_values(self.unit_id)  # type: ignore[union-attr]

    async def get_device_info(self) -> DeviceInfo:
        """Get device metadata (serial number, model, software version).

        This method is only available when using KermiHttpClient.

        Returns:
            DeviceInfo with serial number, model, and software version

        Raises:
            AttributeError: If using Modbus client
        """
        if not self._is_http_client():
            raise AttributeError("get_device_info() is only available with KermiHttpClient.")
        return await self.client.get_device_info(self.unit_id)  # type: ignore[union-attr]
