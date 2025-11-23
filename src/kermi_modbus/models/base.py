"""Base device class for all Kermi Modbus devices."""

import logging
from typing import Any

from ..client import KermiModbusClient
from ..exceptions import ReadOnlyRegisterError, ValidationError
from ..registers import RegisterDef
from ..types import BooleanValue, UnitId

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
        """
        raw_value = await self.client.read_register(
            address=register.address,
            unit_id=self.unit_id,
        )

        # Handle type conversion
        if isinstance(raw_value, list):
            raw_value = raw_value[0]

        if register.data_type == "bool":
            return bool(raw_value)
        elif register.data_type == "enum":
            return raw_value
        elif register.converter:
            return register.converter(raw_value)
        else:
            return raw_value

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
            raw_value = register.inverse_converter(value)  # type: ignore
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

    async def get_all_readable_values(self) -> dict[str, Any]:
        """Read all readable registers and return as a dictionary.

        Returns:
            Dictionary mapping register names to values

        Note:
            This method reads each register individually, which may be slow.
            Consider using specific getter methods for production use.
        """
        values = {}
        for name, register in self.registers.items():
            if "R" in register.attribute:
                try:
                    values[name] = await self._read_register(register)
                except Exception as e:
                    logger.warning(f"Failed to read {name}: {e}")
                    values[name] = None
        return values
