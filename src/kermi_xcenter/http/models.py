"""Data models for HTTP API responses."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HttpDevice:
    """Device discovered via HTTP API.

    Attributes:
        device_id: UUID string identifying the device
        device_type: Device type code (95=StorageSystem, 97=HeatPump)
        display_name: Human-readable device name
        unit_id: Modbus unit ID (30, 40, 50, 51)
    """

    device_id: str
    device_type: int
    display_name: str
    unit_id: int


@dataclass
class DeviceInfo:
    """Device metadata available via HTTP API.

    Attributes:
        serial_number: Device serial number (e.g., "29-41-00-78-d0-cc")
        model: Device model name (e.g., "x-change dynamic pro")
        software_version: Firmware version as "major.minor.patch"
    """

    serial_number: str
    model: str
    software_version: str


@dataclass
class Alarm:
    """Alarm record from the HTTP API.

    Attributes:
        alarm_id: Unique identifier for the alarm
        timestamp: When the alarm occurred
        message: Alarm description text
        device_id: UUID of the device that raised the alarm
        acknowledged: Whether the alarm has been acknowledged
    """

    alarm_id: str
    timestamp: datetime
    message: str
    device_id: str
    acknowledged: bool


@dataclass
class DatapointConfig:
    """Configuration for a datapoint from HTTP API.

    Attributes:
        config_id: UUID for this datapoint configuration
        well_known_name: Internal name (maps to Python attribute name)
        display_name: German display name from Kermi
        unit: Measurement unit (°C, kW, etc.)
        category: 0=sensor/status, 1=writable setting
        data_type: 0=enum, 1=value, 2=boolean
        min_value: Minimum allowed value (for settings)
        max_value: Maximum allowed value (for settings)
        address: Modbus address string if applicable
    """

    config_id: str
    well_known_name: str | None
    display_name: str
    unit: str
    category: int
    data_type: int
    min_value: float | None = None
    max_value: float | None = None
    address: str | None = None
