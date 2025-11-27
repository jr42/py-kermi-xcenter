"""Async Python interface for Kermi heat pumps via Modbus.

This package provides an async interface to control and monitor Kermi heat pump
systems through the Modbus protocol (TCP or RTU).

Basic usage:
    >>> from kermi_xcenter import KermiModbusClient, HeatPump
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

__version__ = "0.2.1"

from .client import KermiModbusClient
from .exceptions import (
    ConnectionError,
    DataConversionError,
    KermiModbusError,
    ReadOnlyRegisterError,
    RegisterReadError,
    RegisterUnsupportedError,
    RegisterWriteError,
    ValidationError,
)
from .models import HeatPump, KermiDevice, StorageSystem, UniversalModule
from .types import (
    BooleanValue,
    EnergyMode,
    ExternalHeatGeneratorMode,
    ExternalHeatGeneratorStatus,
    HeatingCircuitStatus,
    HeatPumpStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)

__all__ = [
    "__version__",
    # Client
    "KermiModbusClient",
    # Devices
    "KermiDevice",
    "HeatPump",
    "StorageSystem",
    "UniversalModule",
    # Exceptions
    "KermiModbusError",
    "ConnectionError",
    "DataConversionError",
    "RegisterReadError",
    "RegisterUnsupportedError",
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
