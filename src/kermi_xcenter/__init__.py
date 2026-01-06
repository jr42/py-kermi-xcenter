"""Async Python interface for Kermi heat pumps via Modbus and HTTP.

This package provides an async interface to control and monitor Kermi heat pump
systems through the Modbus protocol (TCP or RTU) or HTTP API.

HTTP is recommended for most use cases - it's more efficient and provides access
to more datapoints. Modbus is still available for RTU connections or when HTTP
is not accessible.

HTTP usage (recommended):
    >>> from kermi_xcenter import KermiHttpClient, HeatPump
    >>>
    >>> async def main():
    ...     client = KermiHttpClient(host="192.168.1.100")  # No password needed by default
    ...     heat_pump = HeatPump(client, unit_id=40)
    ...
    ...     async with client:
    ...         temp = await heat_pump.get_outdoor_temperature()
    ...         all_values = await heat_pump.get_all_values()  # Efficient bulk read

Modbus usage:
    >>> from kermi_xcenter import KermiModbusClient, HeatPump
    >>>
    >>> async def main():
    ...     client = KermiModbusClient(host="192.168.1.100")
    ...     heat_pump = HeatPump(client, unit_id=40)
    ...
    ...     async with client:
    ...         temp = await heat_pump.get_outdoor_temperature()
"""

__version__ = "0.3.0"

from .client import KermiModbusClient
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    DataConversionError,
    DatapointNotWritableError,
    HttpError,
    KermiModbusError,
    ReadOnlyRegisterError,
    RegisterReadError,
    RegisterUnsupportedError,
    RegisterWriteError,
    SessionExpiredError,
    ValidationError,
)
from .http import KermiHttpClient
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
    # Clients
    "KermiHttpClient",  # HTTP client (recommended)
    "KermiModbusClient",  # Modbus client
    # Devices
    "KermiDevice",
    "HeatPump",
    "StorageSystem",
    "UniversalModule",
    # Exceptions - General
    "KermiModbusError",
    "ConnectionError",
    "DataConversionError",
    "RegisterReadError",
    "RegisterUnsupportedError",
    "RegisterWriteError",
    "ValidationError",
    "ReadOnlyRegisterError",
    # Exceptions - HTTP
    "HttpError",
    "AuthenticationError",
    "SessionExpiredError",
    "DatapointNotWritableError",
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
