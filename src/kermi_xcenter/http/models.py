"""Data models for HTTP API responses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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


@dataclass
class SceneState:
    """Current execution state of a scene.

    Attributes:
        condition_is_true: Whether scene conditions are currently met
        action_is_running: Whether scene actions are currently executing
        last_check: When conditions were last evaluated
        execution_time_ms: Last action execution time in milliseconds
    """

    condition_is_true: bool
    action_is_running: bool
    last_check: datetime
    execution_time_ms: int


@dataclass
class SceneOverview:
    """Scene metadata without full condition/action details.

    Use this for listing scenes or monitoring status. For full
    scene configuration, use Scene instead.

    Attributes:
        scene_id: UUID identifying the scene
        display_name: Human-readable name
        description: Optional description
        priority: Lower numbers = higher priority
        enabled: Whether the scene is active
        last_update: When the scene was last modified
        state: Current execution state (if available)
    """

    scene_id: str
    display_name: str
    description: str | None
    priority: int
    enabled: bool
    last_update: datetime
    state: SceneState | None = None


@dataclass
class Scene:
    """Full scene with conditions and actions.

    Scenes are automation rules that execute actions when conditions are met.
    The condition_tree_data and action_data are kept as raw dictionaries
    since their structure is complex and varies by condition/action type.

    Attributes:
        scene_id: UUID identifying the scene
        display_name: Human-readable name
        description: Optional description
        priority: Lower numbers = higher priority
        enabled: Whether the scene is active
        last_update: When the scene was last modified
        condition_tree_data: Tree of conditions (AND/OR logic) as raw dict
        action_data: List of actions to execute as raw dicts
    """

    scene_id: str
    display_name: str
    description: str | None
    priority: int
    enabled: bool
    last_update: datetime
    condition_tree_data: dict[str, Any] = field(default_factory=dict)
    action_data: list[dict[str, Any]] | None = None
