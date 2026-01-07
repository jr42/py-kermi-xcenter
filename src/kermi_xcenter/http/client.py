"""HTTP API client for Kermi x-center heat pump systems.

This module provides an async HTTP client that interfaces with the x-center
device's REST API. It offers more efficient bulk reads and access to additional
datapoints not available via Modbus.
"""

import logging
from datetime import datetime
from typing import Any

from ..exceptions import (
    DatapointNotWritableError,
    HttpError,
    RegisterReadError,
    RegisterWriteError,
)
from .mapping import (
    DEVICE_TYPE_TO_UNIT,
    DISPLAYNAME_TO_ATTR,
    WELLKNOWN_TO_ATTR,
    WRITABLE_DATAPOINTS,
)
from .models import Alarm, DatapointConfig, DeviceInfo, HttpDevice, Scene, SceneOverview, SceneState
from .session import HttpSession

logger = logging.getLogger(__name__)


class KermiHttpClient:
    """HTTP API client for Kermi x-center.

    This client provides access to all datapoints available via the x-center
    HTTP API (~250+), which is more than the Modbus interface. It also provides
    efficient bulk reads where a single API call retrieves all values.

    Example:
        ```python
        client = KermiHttpClient(host="192.168.1.100")  # No password needed by default
        async with client:
            # Get all values efficiently (2 API calls for all data)
            values = await client.get_all_values(unit_id=40)
            print(values["outdoor_temperature"])
        ```

    Attributes:
        host: Device hostname or IP address
        password: Optional password (last 4 digits of serial number)
        port: HTTP port (default 80)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        host: str,
        password: str | None = None,
        port: int = 80,
        timeout: float = 10.0,
    ) -> None:
        """Initialize HTTP client.

        Args:
            host: Device hostname or IP address
            password: Optional password (device default is unauthenticated)
            port: HTTP port (default 80)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.password = password
        self.port = port
        self.timeout = timeout
        self._session = HttpSession(host, port, password, timeout)
        self._connected = False
        self._devices: list[HttpDevice] = []
        self._device_map: dict[int, HttpDevice] = {}  # unit_id -> device
        self._datapoint_configs: dict[str, dict[str, DatapointConfig]] = {}  # device_id -> configs

    async def connect(self) -> None:
        """Connect to the device and discover available devices.

        This method:
        1. Establishes an HTTP session (with authentication if password provided)
        2. Discovers all devices connected to the x-center
        3. Caches device information for subsequent requests

        Raises:
            HttpError: If connection or discovery fails
        """
        await self._session.login()
        await self._discover_devices()
        self._connected = True
        logger.info(f"Connected to x-center at {self.host}, found {len(self._devices)} devices")

    async def disconnect(self) -> None:
        """Disconnect from the device and clean up resources."""
        await self._session.close()
        self._connected = False
        self._devices = []
        self._device_map = {}
        self._datapoint_configs = {}

    async def is_connected(self) -> bool:
        """Check if currently connected.

        Returns:
            True if connected and authenticated
        """
        return self._connected and self._session.is_authenticated

    @property
    def devices(self) -> list[HttpDevice]:
        """Get list of discovered devices.

        Returns:
            List of HttpDevice objects
        """
        return self._devices

    async def __aenter__(self) -> "KermiHttpClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()

    # =========================================================================
    # Device Discovery
    # =========================================================================

    async def _discover_devices(self) -> None:
        """Discover all devices connected to the x-center.

        The API returns FavoriteDatapoint items, from which we extract unique devices
        based on DeviceId and DeviceType from the datapoint config.

        The x-center IFM (Interface Module) is always available as device ID
        00000000-0000-0000-0000-000000000000 (unit 0).
        """
        data = await self._session.request(
            "Favorite/GetFavorites/00000000-0000-0000-0000-000000000000",
            {"WithDetails": True, "OnlyHomeScreen": False},
        )

        self._devices = []
        self._device_map = {}

        # Always add the IFM device (the x-center gateway itself)
        # It's always available at device ID 00000000-0000-0000-0000-000000000000
        ifm_device = HttpDevice(
            device_id="00000000-0000-0000-0000-000000000000",
            device_type=0,  # IFM has device type 0
            display_name="x-center IFM",
            unit_id=0,
        )
        self._devices.append(ifm_device)
        self._device_map[0] = ifm_device
        logger.debug("Added IFM device (x-center gateway) at unit 0")

        if not data:
            return

        # Extract unique devices from FavoriteDatapoint items
        seen_devices: dict[str, dict[str, Any]] = {}
        for item in data:
            device_id = item.get("DeviceId")
            if not device_id or device_id == "00000000-0000-0000-0000-000000000000":
                continue

            if device_id in seen_devices:
                continue

            # Get device type from DatapointConfig
            config = item.get("DatapointConfig", {})
            device_type = config.get("DeviceType")

            seen_devices[device_id] = {"device_type": device_type}

        # For devices without type, query their bundles to determine type
        for device_id, info in seen_devices.items():
            if info["device_type"] is None:
                device_type = await self._get_device_type_from_bundles(device_id)
                info["device_type"] = device_type

        # Determine unit IDs and create device objects
        # Sort by device_type to ensure HeatPump (97) comes before StorageSystem (95)
        storage_count = 0
        for device_id, info in sorted(
            seen_devices.items(), key=lambda x: x[1].get("device_type") or 0, reverse=True
        ):
            device_type = info["device_type"]

            # Determine unit_id from device type
            if device_type == 97:  # HeatPump
                unit_id = 40
                display_name = "Heat Pump"
            elif device_type == 95:  # StorageSystem
                # First storage is heating (50), second is hot water (51)
                unit_id = 50 + storage_count
                display_name = "Heating Storage" if storage_count == 0 else "Hot Water Storage"
                storage_count += 1
            else:
                unit_id = DEVICE_TYPE_TO_UNIT.get(device_type or 0, 40)
                display_name = "Unknown Device"

            device = HttpDevice(
                device_id=device_id,
                device_type=device_type or 0,
                display_name=display_name,
                unit_id=unit_id,
            )
            self._devices.append(device)
            self._device_map[unit_id] = device

            logger.debug(f"Discovered device: {display_name} (unit {unit_id}, type {device_type})")

    async def _get_device_type_from_bundles(self, device_id: str) -> int | None:
        """Get device type by querying bundles for a device.

        Args:
            device_id: Device UUID

        Returns:
            Device type (95 or 97) or None if not found
        """
        try:
            bundles = await self._session.request(
                "Menu/GetBundlesByCategory",
                {"DeviceId": device_id, "Category": 0},
            )
            if bundles:
                for bundle in bundles:
                    for dp in bundle.get("Datapoints", []):
                        config = dp.get("Config", {})
                        device_type = config.get("DeviceType")
                        if device_type is not None:
                            return int(device_type)
        except Exception as e:
            logger.debug(f"Could not determine device type for {device_id}: {e}")
        return None

    def _get_device(self, unit_id: int) -> HttpDevice:
        """Get device by unit ID.

        Args:
            unit_id: Modbus unit ID (30, 40, 50, 51)

        Returns:
            HttpDevice for the unit

        Raises:
            HttpError: If device not found
        """
        if unit_id not in self._device_map:
            raise HttpError(f"Device with unit_id {unit_id} not found")
        return self._device_map[unit_id]

    # =========================================================================
    # Bulk Read Operations
    # =========================================================================

    async def get_all_values(self, unit_id: int) -> dict[str, Any]:
        """Get all datapoint values for a device efficiently.

        This is the most efficient way to read data - a single API call
        retrieves all datapoints for the device (both Category 0 and 1).

        Args:
            unit_id: Modbus unit ID (30, 40, 50, 51)

        Returns:
            Dict mapping Python attribute names to values

        Raises:
            HttpError: If the request fails
        """
        device = self._get_device(unit_id)
        values: dict[str, Any] = {}

        # Fetch both categories (0=sensors, 1=settings)
        for category in [0, 1]:
            bundles = await self._session.request(
                "Menu/GetBundlesByCategory",
                {"DeviceId": device.device_id, "Category": category},
            )

            if not bundles:
                continue

            for bundle in bundles:
                for datapoint in bundle.get("Datapoints", []):
                    config = datapoint.get("Config", {})
                    value_data = datapoint.get("DatapointValue", {})

                    well_known_name = config.get("WellKnownName")
                    display_name = config.get("DisplayName", "")

                    # Try WellKnownName mapping first, then DisplayName fallback
                    attr_name = None
                    if well_known_name:
                        attr_name = WELLKNOWN_TO_ATTR.get(well_known_name)
                    if not attr_name and display_name:
                        attr_name = DISPLAYNAME_TO_ATTR.get(display_name)

                    if attr_name:
                        values[attr_name] = value_data.get("Value")

                    # Also cache the config for write operations
                    config_id = config.get("DatapointConfigId")
                    if config_id and device.device_id not in self._datapoint_configs:
                        self._datapoint_configs[device.device_id] = {}

                    if config_id and attr_name:
                        self._datapoint_configs[device.device_id][attr_name] = DatapointConfig(
                            config_id=config_id,
                            well_known_name=well_known_name or "",
                            display_name=display_name,
                            unit=config.get("Unit", ""),
                            category=config.get("Category", 0),
                            data_type=config.get("DatapointType", 1),
                            min_value=config.get("MinValue"),
                            max_value=config.get("MaxValue"),
                            address=config.get("Address"),
                        )

        return values

    async def get_value(self, name: str, unit_id: int) -> Any:
        """Get a single datapoint value by Python attribute name.

        Note: This fetches all values and returns one. For multiple reads,
        use get_all_values() directly for efficiency.

        Args:
            name: Python attribute name (e.g., "outdoor_temperature")
            unit_id: Modbus unit ID (30, 40, 50, 51)

        Returns:
            The datapoint value

        Raises:
            RegisterReadError: If the datapoint is not found
        """
        values = await self.get_all_values(unit_id)
        if name not in values:
            raise RegisterReadError(0, f"Datapoint '{name}' not found")
        return values[name]

    # =========================================================================
    # Modbus Compatibility Interface
    # =========================================================================

    async def read_register(
        self, address: int, unit_id: int, count: int = 1  # noqa: ARG002
    ) -> int:
        """Read a Modbus register (compatibility interface).

        This method provides compatibility with the Modbus client interface.
        It fetches all values and returns the one matching the address.

        Note: This is less efficient than get_all_values() for multiple reads.

        Args:
            address: Modbus register address
            unit_id: Modbus unit ID
            count: Number of registers (only 1 supported)

        Returns:
            Register value as integer

        Raises:
            RegisterReadError: If register not found
        """
        # For HTTP, we don't have direct register access
        # We need to map address to WellKnownName via the cached configs
        values = await self.get_all_values(unit_id)

        # Search for a datapoint with matching address
        device = self._get_device(unit_id)
        configs = self._datapoint_configs.get(device.device_id, {})

        for attr_name, config in configs.items():
            if config.address and str(address) in config.address:
                value = values.get(attr_name)
                if value is not None:
                    # Convert to int for Modbus compatibility
                    if isinstance(value, bool):
                        return 1 if value else 0
                    if isinstance(value, (int, float)):
                        return int(value)
        raise RegisterReadError(address, "Register address not found in HTTP datapoints")

    async def write_register(self, address: int, value: int, unit_id: int) -> None:
        """Write to a Modbus register (compatibility interface).

        This method provides compatibility with the Modbus client interface.
        It maps the register address to the corresponding HTTP datapoint.

        Args:
            address: Modbus register address
            value: Value to write
            unit_id: Modbus unit ID

        Raises:
            RegisterWriteError: If register not found or not writable
        """
        device = self._get_device(unit_id)
        configs = self._datapoint_configs.get(device.device_id, {})

        # Find the datapoint by address
        for attr_name, config in configs.items():
            if config.address and str(address) in config.address:
                # Check if writable
                if attr_name not in WRITABLE_DATAPOINTS:
                    raise RegisterWriteError(
                        address, value, f"Datapoint '{attr_name}' is not writable"
                    )

                await self._write_datapoint(device.device_id, config.config_id, value)
                return

        raise RegisterWriteError(address, value, "Register address not found in HTTP datapoints")

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def set_value(self, name: str, value: Any, unit_id: int) -> None:
        """Set a datapoint value by Python attribute name.

        Only user-facing settings can be written. Attempting to write to
        read-only or restricted datapoints will raise an error.

        Args:
            name: Python attribute name (e.g., "hot_water_boost_active")
            value: Value to write
            unit_id: Modbus unit ID

        Raises:
            DatapointNotWritableError: If datapoint is not writable
            HttpError: If write fails
        """
        if name not in WRITABLE_DATAPOINTS:
            raise DatapointNotWritableError(name)

        device = self._get_device(unit_id)

        # Ensure we have configs cached
        if device.device_id not in self._datapoint_configs:
            await self.get_all_values(unit_id)

        configs = self._datapoint_configs.get(device.device_id, {})
        if name not in configs:
            raise HttpError(f"Datapoint '{name}' not found")

        config = configs[name]
        await self._write_datapoint(device.device_id, config.config_id, value)

    async def _write_datapoint(self, device_id: str, config_id: str, value: Any) -> None:
        """Write a value to a datapoint.

        Args:
            device_id: Device UUID
            config_id: Datapoint config UUID
            value: Value to write
        """
        await self._session.request(
            "Datapoint/WriteValues",
            {
                "DatapointValues": [
                    {
                        "DatapointConfigId": config_id,
                        "DeviceId": device_id,
                        "Value": value,
                    }
                ]
            },
        )
        logger.debug(f"Wrote value {value} to datapoint {config_id}")

    # =========================================================================
    # Device Info
    # =========================================================================

    async def get_device_info(self, unit_id: int) -> DeviceInfo:
        """Get device metadata (serial number, model, software version).

        Args:
            unit_id: Modbus unit ID (0 for IFM, 40 for Heat Pump, 50/51 for Storage)

        Returns:
            DeviceInfo with serial number, model, and software version
        """
        values = await self.get_all_values(unit_id)
        device = self._get_device(unit_id)

        # Get software version and model based on device type
        if unit_id == 0:  # IFM (x-center gateway)
            software_version = str(values.get("ifm_software_version", ""))
            serial_number = str(values.get("ifm_serial_number", ""))
            model = "x-center IFM"
        elif unit_id == 40:  # Heat Pump
            major = values.get("software_version_major", 0)
            minor = values.get("software_version_minor", 0)
            patch = values.get("software_version_patch", 0)
            software_version = f"{major}.{minor}.{patch}"
            serial_number = str(values.get("serial_number", ""))
            model = (
                values.get("heat_pump_model") or values.get("device_name") or device.display_name
            )
        else:  # Storage System
            major = values.get("power_module_sw_major", 0)
            minor = values.get("power_module_sw_minor", 0)
            patch = values.get("power_module_sw_patch", 0)
            software_version = f"{major}.{minor}.{patch}"
            serial_number = str(values.get("serial_number", ""))
            model = values.get("device_type_name") or device.display_name

        return DeviceInfo(
            serial_number=serial_number,
            model=str(model) if model else "",
            software_version=software_version,
        )

    # =========================================================================
    # Alarms
    # =========================================================================

    async def get_current_alarms(self) -> list[Alarm]:
        """Get current active alarms.

        Returns:
            List of active Alarm objects
        """
        data = await self._session.request("Alarm/GetCurrentAlarms", {})
        return self._parse_alarms(data)

    async def get_alarm_history(self) -> list[Alarm]:
        """Get alarm history.

        Returns:
            List of historical Alarm objects
        """
        data = await self._session.request("Alarm/GetAlarmHistory", {})
        return self._parse_alarms(data)

    def _parse_alarms(self, data: Any) -> list[Alarm]:
        """Parse alarm data from API response.

        Args:
            data: Alarm data from API

        Returns:
            List of Alarm objects
        """
        alarms: list[Alarm] = []
        if not data:
            return alarms

        for item in data:
            try:
                timestamp_str = item.get("Timestamp", "")
                timestamp = (
                    datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if timestamp_str
                    else datetime.now()
                )

                alarms.append(
                    Alarm(
                        alarm_id=str(item.get("AlarmId", "")),
                        timestamp=timestamp,
                        message=str(item.get("Message", "")),
                        device_id=str(item.get("DeviceId", "")),
                        acknowledged=bool(item.get("Acknowledged", False)),
                    )
                )
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse alarm: {e}")
                continue

        return alarms

    async def clear_current_alarms(self) -> None:
        """Acknowledge/clear current active alarms."""
        await self._session.request("Alarm/ClearCurrentAlarms", {})

    async def reconnect(self) -> None:
        """Reconnect to the device.

        For HTTP, this just re-establishes the session. The session
        handles automatic re-authentication, so this is mostly a no-op.
        """
        await self._session.close()
        await self._session.login()
        logger.debug("HTTP session reconnected")

    # =========================================================================
    # Scenes
    # =========================================================================

    async def get_scenes(self) -> list[SceneOverview]:
        """Get all scenes configured on the device.

        Uses GetScenesByDeviceId with the IFM device ID as a workaround,
        since GetAllScenes returns 405 on local devices.

        Returns:
            List of SceneOverview objects with scene metadata

        Example:
            ```python
            scenes = await client.get_scenes()
            for scene in scenes:
                print(f"{scene.display_name}: enabled={scene.enabled}")
            ```
        """
        # Use IFM device ID to get all scenes (workaround for GetAllScenes 405)
        data = await self._session.request(
            "Scene/GetScenesByDeviceId",
            {"DeviceId": "00000000-0000-0000-0000-000000000000"},
        )

        scenes: list[SceneOverview] = []
        if not data:
            return scenes

        for item in data:
            try:
                last_update_str = item.get("LastUpdateUtc", "")
                last_update = (
                    datetime.fromisoformat(last_update_str.replace("Z", "+00:00"))
                    if last_update_str
                    else datetime.now()
                )

                scenes.append(
                    SceneOverview(
                        scene_id=str(item.get("SceneId", "")),
                        display_name=str(item.get("DisplayName", "")),
                        description=item.get("Description"),
                        priority=int(item.get("Priority", 1000)),
                        enabled=bool(item.get("Enabled", False)),
                        last_update=last_update,
                        state=None,  # Not included in list response
                    )
                )
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse scene: {e}")
                continue

        return scenes

    async def get_scene(self, scene_id: str) -> Scene:
        """Get full scene configuration by ID.

        Returns the complete scene including conditions and actions.

        Args:
            scene_id: UUID of the scene

        Returns:
            Scene object with full configuration

        Raises:
            HttpError: If scene not found or request fails
        """
        data = await self._session.request(
            "Scene/GetSceneById",
            {"SceneId": scene_id},
        )

        if not data:
            raise HttpError(f"Scene {scene_id} not found")

        last_update_str = data.get("LastUpdateUtc", "")
        last_update = (
            datetime.fromisoformat(last_update_str.replace("Z", "+00:00"))
            if last_update_str
            else datetime.now()
        )

        return Scene(
            scene_id=str(data.get("SceneId", "")),
            display_name=str(data.get("DisplayName", "")),
            description=data.get("Description"),
            priority=int(data.get("Priority", 1000)),
            enabled=bool(data.get("Enabled", False)),
            last_update=last_update,
            condition_tree_data=data.get("ConditionTreeData", {}),
            action_data=data.get("ActionDataForSerialization"),
        )

    async def get_scene_state(self, scene_id: str) -> SceneState:
        """Get current execution state of a scene.

        Returns whether conditions are met and if actions are running.

        Args:
            scene_id: UUID of the scene

        Returns:
            SceneState with condition and action status

        Raises:
            HttpError: If scene not found or request fails
        """
        data = await self._session.request(
            "Scene/GetSceneOverviewById",
            {"SceneId": scene_id},
        )

        if not data:
            raise HttpError(f"Scene {scene_id} not found")

        state_data = data.get("SceneState", {})
        last_check_str = state_data.get("LastConditionCheckUtc", "")
        last_check = (
            datetime.fromisoformat(last_check_str.replace("Z", "+00:00"))
            if last_check_str
            else datetime.now()
        )

        return SceneState(
            condition_is_true=bool(state_data.get("ConditionIsTrue", False)),
            action_is_running=bool(state_data.get("ActionIsRunning", False)),
            last_check=last_check,
            execution_time_ms=int(state_data.get("ExecutionTimeMs", 0)),
        )

    async def execute_scene(self, scene_id: str) -> None:
        """Execute a scene's actions immediately.

        This triggers all actions defined in the scene regardless of
        whether conditions are met. Use with caution.

        Args:
            scene_id: UUID of the scene to execute

        Raises:
            HttpError: If execution fails

        Example:
            ```python
            # Trigger "Night Mode" scene
            await client.execute_scene("f29e1596-5efb-4b5e-8674-5baf2b65a377")
            ```
        """
        await self._session.request(
            "Scene/ExecuteScene",
            {"SceneId": scene_id},
        )
        logger.info(f"Executed scene {scene_id}")
