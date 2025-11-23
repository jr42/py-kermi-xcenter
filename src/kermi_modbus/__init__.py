"""Async Python interface for Kermi heat pumps via Modbus.

This package provides an async interface to control and monitor Kermi heat pump
systems through the Modbus protocol (TCP or RTU).

Basic usage:
    >>> from kermi_modbus import KermiModbusClient, HeatPump
    >>>
    >>> async def main():
    ...     client = KermiModbusClient(host="192.168.1.100")
    ...     heat_pump = HeatPump(client, unit_id=40)
    ...
    ...     async with client:
    ...         temp = await heat_pump.get_outdoor_temperature()
    ...         cop = await heat_pump.get_cop_total()
    ...         print(f"Outdoor: {temp}°C, COP: {cop}")
"""

__version__ = "0.1.0"

from .client import KermiModbusClient
from .exceptions import (
    ConnectionError,
    KermiModbusError,
    ReadOnlyRegisterError,
    RegisterReadError,
    RegisterWriteError,
    ValidationError,
)
from .models.base import KermiDevice
from .types import (
    BooleanValue,
    EnergyMode,
    ExternalHeatGeneratorMode,
    ExternalHeatGeneratorStatus,
    HeatPumpStatus,
    HeatingCircuitStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)

__all__ = [
    "__version__",
    # Client
    "KermiModbusClient",
    # Base device
    "KermiDevice",
    # Exceptions
    "KermiModbusError",
    "ConnectionError",
    "RegisterReadError",
    "RegisterWriteError",
    "ValidationError",
    "ReadOnlyRegisterError",
    # Enums
    "HeatPumpStatus",
    "HeatingCircuitStatus",
    "OperatingMode",
    "OperatingType",
    "EnergyMode",
    "SeasonSelection",
    "ExternalHeatGeneratorMode",
    "ExternalHeatGeneratorStatus",
    "BooleanValue",
]
