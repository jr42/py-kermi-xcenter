"""Base device class for all Kermi Modbus devices."""

import logging
from typing import Any

from ..client import KermiModbusClient
from ..exceptions import (
    ConnectionError,
    DataConversionError,
    ReadOnlyRegisterError,
    RegisterReadError,
    RegisterUnsupportedError,
    ValidationError,
)
from ..registers import RegisterDef
from ..types import UnitId

logger = logging.getLogger(__name__)


class KermiDevice:
    """Base class for Kermi Modbus devices.

    Provides common functionality for reading and writing registers
    with automatic data type conversion and validation.

    Attributes:
        client: Modbus client instance
        unit_id: Modbus unit ID for this device
        registers: Dictionary of register definitions for this device
    """

    def __init__(
        self,
        client: KermiModbusClient,
        unit_id: UnitId,
        registers: dict[str, RegisterDef],
    ) -> None:
        """Initialize the device.

        Args:
            client: Modbus client instance
            unit_id: Modbus unit ID
            registers: Register definitions for this device
        """
        self.client = client
        self.unit_id = unit_id
        self.registers = registers

    async def _read_register(self, register: RegisterDef) -> float | int | bool:
        """Read a register and convert to engineering units.

        Args:
            register: Register definition

        Returns:
            Converted value in engineering units (or bool for boolean registers)

        Raises:
            RegisterReadError: If read fails
            RegisterUnsupportedError: If register not available on this device
            DataConversionError: If conversion to engineering units fails
        """
        try:
            raw_value = await self.client.read_register(
                address=register.address,
                unit_id=self.unit_id,
            )
        except Exception as e:
            # Check if this is a protocol-level error indicating unsupported register
            if self._is_unsupported_register_error(e):
                raise RegisterUnsupportedError(
                    register.name, "Device returned malformed response"
                ) from e
            # Re-raise other errors as-is
            raise

        # Handle type conversion
        if isinstance(raw_value, list):
            if not raw_value:
                # Empty response - treat as unsupported
                raise RegisterUnsupportedError(register.name, "Device returned empty response")
            raw_value = raw_value[0]

        # Wrap converter exceptions
        try:
            if register.data_type == "bool":
                return bool(raw_value)
            elif register.data_type == "enum":
                return raw_value
            elif register.converter:
                return register.converter(raw_value)
            else:
                return raw_value
        except (TypeError, ValueError, ArithmeticError) as e:
            raise DataConversionError(register.name, raw_value, f"{type(e).__name__}: {e}") from e

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

    async def get_all_readable_values(self) -> dict[str, Any]:
        """Read all readable registers and return as a dictionary.

        Returns:
            Dictionary mapping register names to values.
            Unsupported or failed registers are set to None.

        Note:
            This method reads each register individually, which may be slow.
            Consider using specific getter methods for production use.

            This method is designed to be resilient to firmware variations
            and will continue reading other registers even if some fail.
            Check logs for warnings about unsupported registers.

            If a protocol error corrupts the connection (e.g., malformed Modbus frame),
            this method will automatically reconnect to recover.
        """
        values: dict[str, Any] = {}
        unsupported_registers: list[str] = []

        for name, register in self.registers.items():
            if "R" not in register.attribute:
                continue

            try:
                values[name] = await self._read_register(register)

            except RegisterUnsupportedError:
                # Data point not available on this device/firmware - this is expected
                logger.info(
                    f"Data point '{name}' not available on this device. "
                    f"This is normal for some device models/firmware versions."
                )
                values[name] = None
                unsupported_registers.append(name)

                # Reconnect to recover from connection corruption caused by malformed frame
                try:
                    logger.debug("Reconnecting after malformed frame...")
                    await self.client.reconnect()
                except Exception as reconnect_error:
                    logger.warning(
                        f"Reconnection failed: {reconnect_error}. "
                        f"Continuing with existing connection..."
                    )

            except DataConversionError as e:
                # Converter failed - data read OK but conversion failed
                logger.warning(
                    f"Failed to convert '{name}' (raw value {e.raw_value}): {e}. "
                    f"This may indicate unexpected firmware behavior."
                )
                values[name] = None

            except (RegisterReadError, ConnectionError, ValidationError) as e:
                # Standard errors
                logger.warning(f"Failed to read '{name}': {type(e).__name__}: {e}")
                values[name] = None

            except Exception as e:
                # Catch-all for truly unexpected errors
                logger.error(
                    f"Unexpected error reading '{name}': {type(e).__name__}: {e}",
                    exc_info=True,
                )
                values[name] = None

        # Summary logging for unsupported data points
        if unsupported_registers:
            logger.info(
                f"{len(unsupported_registers)} data point(s) not supported by this device: "
                f"{', '.join(unsupported_registers)}"
            )

        return values
