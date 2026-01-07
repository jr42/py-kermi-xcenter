"""Tests for HTTP client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kermi_xcenter import (
    DatapointNotWritableError,
    HttpError,
    KermiHttpClient,
)
from kermi_xcenter.http.models import (
    Alarm,
    DatapointConfig,
    DeviceInfo,
    HttpDevice,
    Scene,
    SceneOverview,
    SceneState,
)


class TestHttpClientCreation:
    """Test HTTP client initialization."""

    def test_http_client_creation_minimal(self):
        """Test creating HTTP client with minimal parameters."""
        client = KermiHttpClient(host="192.168.1.100")
        assert client.host == "192.168.1.100"
        assert client.password is None
        assert client.port == 80
        assert client.timeout == 10.0

    def test_http_client_creation_with_password(self):
        """Test creating HTTP client with password."""
        client = KermiHttpClient(host="192.168.1.100", password="1234")
        assert client.host == "192.168.1.100"
        assert client.password == "1234"

    def test_http_client_creation_custom_port(self):
        """Test creating HTTP client with custom port."""
        client = KermiHttpClient(host="192.168.1.100", port=8080, timeout=30.0)
        assert client.port == 8080
        assert client.timeout == 30.0


class TestHttpClientConnection:
    """Test HTTP client connection methods."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance."""
        return KermiHttpClient(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_connect_success(self, http_client):
        """Test successful connection and device discovery."""
        with (
            patch.object(http_client._session, "login", new_callable=AsyncMock) as mock_login,
            patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request,
        ):
            # New format: FavoriteDatapoint items with DeviceId and DatapointConfig
            mock_request.return_value = [
                {
                    "DeviceId": "device-uuid-1",
                    "DatapointConfig": {
                        "DeviceType": 97,  # HeatPump
                        "DisplayName": "Outdoor Temperature",
                    },
                },
                {
                    "DeviceId": "device-uuid-2",
                    "DatapointConfig": {
                        "DeviceType": 95,  # StorageSystem
                        "DisplayName": "Heating Storage Temp",
                    },
                },
            ]

            await http_client.connect()

            mock_login.assert_called_once()
            assert http_client._connected is True
            # 3 devices: IFM (always added) + 2 from favorites
            assert len(http_client.devices) == 3

    @pytest.mark.asyncio
    async def test_disconnect(self, http_client):
        """Test disconnection."""
        http_client._connected = True
        http_client._devices = [MagicMock()]
        http_client._device_map = {40: MagicMock()}

        with patch.object(http_client._session, "close", new_callable=AsyncMock) as mock_close:
            await http_client.disconnect()

            mock_close.assert_called_once()
            assert http_client._connected is False
            assert len(http_client._devices) == 0
            assert len(http_client._device_map) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self, http_client):
        """Test async context manager."""
        with (
            patch.object(http_client, "connect", new_callable=AsyncMock) as mock_connect,
            patch.object(http_client, "disconnect", new_callable=AsyncMock) as mock_disconnect,
        ):
            async with http_client:
                mock_connect.assert_called_once()

            mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_connected(self, http_client):
        """Test connection status check."""
        http_client._connected = True
        http_client._session._authenticated = True

        result = await http_client.is_connected()
        assert result is True

    @pytest.mark.asyncio
    async def test_is_not_connected(self, http_client):
        """Test connection status when not connected."""
        http_client._connected = False

        result = await http_client.is_connected()
        assert result is False


class TestHttpClientDeviceDiscovery:
    """Test device discovery functionality."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance."""
        return KermiHttpClient(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_discover_heat_pump(self, http_client):
        """Test discovering a heat pump device."""
        with (
            patch.object(http_client._session, "login", new_callable=AsyncMock),
            patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request,
        ):
            # New format: FavoriteDatapoint items
            mock_request.return_value = [
                {
                    "DeviceId": "hp-uuid",
                    "DatapointConfig": {
                        "DeviceType": 97,
                        "DisplayName": "Heat Pump Status",
                    },
                }
            ]

            await http_client.connect()

            # 2 devices: IFM (always added) + Heat Pump from favorites
            assert len(http_client.devices) == 2
            # IFM is first (unit 0), Heat Pump is second (unit 40)
            assert http_client.devices[0].unit_id == 0  # IFM
            assert http_client.devices[1].device_type == 97
            assert http_client.devices[1].unit_id == 40  # HeatPump unit

    @pytest.mark.asyncio
    async def test_discover_storage_system(self, http_client):
        """Test discovering storage system devices."""
        with (
            patch.object(http_client._session, "login", new_callable=AsyncMock),
            patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request,
        ):
            # New format: FavoriteDatapoint items
            mock_request.return_value = [
                {
                    "DeviceId": "ss-uuid-1",
                    "DatapointConfig": {
                        "DeviceType": 95,
                        "DisplayName": "Heating Storage Temp",
                    },
                },
                {
                    "DeviceId": "ss-uuid-2",
                    "DatapointConfig": {
                        "DeviceType": 95,
                        "DisplayName": "Hot Water Storage Temp",
                    },
                },
            ]

            await http_client.connect()

            # 3 devices: IFM (always added) + 2 StorageSystems from favorites
            assert len(http_client.devices) == 3
            # IFM is first (unit 0), then storage units 50 and 51
            assert http_client.devices[0].unit_id == 0  # IFM
            assert http_client.devices[1].unit_id == 50
            assert http_client.devices[2].unit_id == 51

    @pytest.mark.asyncio
    async def test_get_device_not_found(self, http_client):
        """Test getting a device that doesn't exist."""
        http_client._device_map = {}

        with pytest.raises(HttpError, match="Device with unit_id 40 not found"):
            http_client._get_device(40)


class TestHttpClientReadOperations:
    """Test HTTP client read operations."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client with a mock device."""
        client = KermiHttpClient(host="192.168.1.100")
        client._device_map = {
            40: HttpDevice(
                device_id="hp-uuid",
                device_type=97,
                display_name="Heat Pump",
                unit_id=40,
            )
        }
        client._connected = True
        return client

    @pytest.mark.asyncio
    async def test_get_all_values(self, http_client):
        """Test getting all datapoint values."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            # Mock response for category 0 and 1
            mock_request.side_effect = [
                # Category 0 (sensors)
                [
                    {
                        "Datapoints": [
                            {
                                "Config": {
                                    "WellKnownName": "LuftTemperatur",
                                    "DatapointConfigId": "config-1",
                                    "DisplayName": "Outdoor Temperature",
                                    "Unit": "°C",
                                    "Category": 0,
                                },
                                "DatapointValue": {"Value": 15.5},
                            }
                        ]
                    }
                ],
                # Category 1 (settings)
                [
                    {
                        "Datapoints": [
                            {
                                "Config": {
                                    "WellKnownName": "BufferSystem_OneTimeTwe",
                                    "DatapointConfigId": "config-2",
                                    "DisplayName": "One-time Hot Water",
                                    "Unit": "",
                                    "Category": 1,
                                },
                                "DatapointValue": {"Value": False},
                            }
                        ]
                    }
                ],
            ]

            values = await http_client.get_all_values(unit_id=40)

            assert "outdoor_temperature" in values
            assert values["outdoor_temperature"] == 15.5
            assert "hot_water_boost_active" in values
            assert values["hot_water_boost_active"] is False

    @pytest.mark.asyncio
    async def test_get_value(self, http_client):
        """Test getting a single value."""
        with patch.object(http_client, "get_all_values", new_callable=AsyncMock) as mock_get_all:
            mock_get_all.return_value = {"outdoor_temperature": 18.0}

            value = await http_client.get_value("outdoor_temperature", unit_id=40)

            assert value == 18.0

    @pytest.mark.asyncio
    async def test_get_value_not_found(self, http_client):
        """Test getting a value that doesn't exist."""
        with patch.object(http_client, "get_all_values", new_callable=AsyncMock) as mock_get_all:
            mock_get_all.return_value = {}

            from kermi_xcenter import RegisterReadError

            with pytest.raises(RegisterReadError, match="Datapoint 'unknown_datapoint' not found"):
                await http_client.get_value("unknown_datapoint", unit_id=40)


class TestHttpClientWriteOperations:
    """Test HTTP client write operations."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client with mock device and configs."""
        client = KermiHttpClient(host="192.168.1.100")
        client._device_map = {
            40: HttpDevice(
                device_id="hp-uuid",
                device_type=97,
                display_name="Heat Pump",
                unit_id=40,
            )
        }
        client._datapoint_configs = {
            "hp-uuid": {
                "hot_water_boost_active": DatapointConfig(
                    config_id="config-boost",
                    well_known_name="BufferSystem_OneTimeTwe",
                    display_name="One-time Hot Water",
                    unit="",
                    category=1,
                    data_type=1,
                    min_value=None,
                    max_value=None,
                    address=None,
                ),
            }
        }
        client._connected = True
        return client

    @pytest.mark.asyncio
    async def test_set_value(self, http_client):
        """Test setting a writable value."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None

            await http_client.set_value("hot_water_boost_active", True, unit_id=40)

            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "Datapoint/WriteValues"
            assert call_args[0][1]["DatapointValues"][0]["Value"] is True

    @pytest.mark.asyncio
    async def test_set_value_not_writable(self, http_client):
        """Test setting a non-writable value raises error."""
        with pytest.raises(DatapointNotWritableError):
            await http_client.set_value("outdoor_temperature", 20.0, unit_id=40)


class TestHttpClientDeviceInfo:
    """Test device info retrieval."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client with mock device."""
        client = KermiHttpClient(host="192.168.1.100")
        client._device_map = {
            40: HttpDevice(
                device_id="hp-uuid",
                device_type=97,
                display_name="x-change dynamic pro",
                unit_id=40,
            )
        }
        client._connected = True
        return client

    @pytest.mark.asyncio
    async def test_get_device_info(self, http_client):
        """Test getting device info."""
        with patch.object(http_client, "get_all_values", new_callable=AsyncMock) as mock_get_all:
            mock_get_all.return_value = {
                "serial_number": "12345678",
                "software_version_major": 1,
                "software_version_minor": 2,
                "software_version_patch": 3,
            }

            info = await http_client.get_device_info(unit_id=40)

            assert isinstance(info, DeviceInfo)
            assert info.serial_number == "12345678"
            assert info.software_version == "1.2.3"
            assert info.model == "x-change dynamic pro"


class TestHttpClientAlarms:
    """Test alarm functionality."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance."""
        return KermiHttpClient(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_get_current_alarms(self, http_client):
        """Test getting current alarms."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {
                    "AlarmId": "alarm-1",
                    "Timestamp": "2024-01-15T10:30:00Z",
                    "Message": "Low pressure warning",
                    "DeviceId": "hp-uuid",
                    "Acknowledged": False,
                }
            ]

            alarms = await http_client.get_current_alarms()

            assert len(alarms) == 1
            assert isinstance(alarms[0], Alarm)
            assert alarms[0].alarm_id == "alarm-1"
            assert alarms[0].message == "Low pressure warning"
            assert alarms[0].acknowledged is False

    @pytest.mark.asyncio
    async def test_get_alarm_history(self, http_client):
        """Test getting alarm history."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {
                    "AlarmId": "alarm-old",
                    "Timestamp": "2024-01-10T08:00:00Z",
                    "Message": "Previous alarm",
                    "DeviceId": "hp-uuid",
                    "Acknowledged": True,
                }
            ]

            alarms = await http_client.get_alarm_history()

            assert len(alarms) == 1
            assert alarms[0].acknowledged is True

    @pytest.mark.asyncio
    async def test_clear_current_alarms(self, http_client):
        """Test clearing current alarms."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            await http_client.clear_current_alarms()

            mock_request.assert_called_once_with("Alarm/ClearCurrentAlarms", {})

    @pytest.mark.asyncio
    async def test_parse_alarms_empty(self, http_client):
        """Test parsing empty alarm list."""
        alarms = http_client._parse_alarms(None)
        assert alarms == []

    @pytest.mark.asyncio
    async def test_parse_alarms_invalid_data(self, http_client):
        """Test parsing alarms with invalid data."""
        # Should not raise, just skip invalid entries
        alarms = http_client._parse_alarms([{"InvalidKey": "value"}])
        assert len(alarms) == 1  # Still creates alarm with defaults


class TestHttpClientReconnect:
    """Test reconnection functionality."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance."""
        return KermiHttpClient(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_reconnect(self, http_client):
        """Test reconnecting to device."""
        with (
            patch.object(http_client._session, "close", new_callable=AsyncMock) as mock_close,
            patch.object(http_client._session, "login", new_callable=AsyncMock) as mock_login,
        ):
            await http_client.reconnect()

            mock_close.assert_called_once()
            mock_login.assert_called_once()


class TestHttpClientModbusCompatibility:
    """Test Modbus compatibility interface."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client with mock device and address-mapped config."""
        client = KermiHttpClient(host="192.168.1.100")
        client._device_map = {
            40: HttpDevice(
                device_id="hp-uuid",
                device_type=97,
                display_name="Heat Pump",
                unit_id=40,
            )
        }
        client._datapoint_configs = {
            "hp-uuid": {
                "outdoor_temperature": DatapointConfig(
                    config_id="config-temp",
                    well_known_name="LuftTemperatur",
                    display_name="Outdoor Temperature",
                    unit="°C",
                    category=0,
                    data_type=1,
                    min_value=None,
                    max_value=None,
                    address="100",  # Modbus register address
                ),
            }
        }
        client._connected = True
        return client

    @pytest.mark.asyncio
    async def test_read_register_by_address(self, http_client):
        """Test reading by Modbus register address."""
        with patch.object(http_client, "get_all_values", new_callable=AsyncMock) as mock_get_all:
            mock_get_all.return_value = {"outdoor_temperature": 15.5}

            value = await http_client.read_register(address=100, unit_id=40)

            assert value == 15

    @pytest.mark.asyncio
    async def test_read_register_address_not_found(self, http_client):
        """Test reading non-existent register address."""
        with patch.object(http_client, "get_all_values", new_callable=AsyncMock) as mock_get_all:
            mock_get_all.return_value = {"outdoor_temperature": 15.5}

            from kermi_xcenter import RegisterReadError

            with pytest.raises(RegisterReadError, match="Register address not found"):
                await http_client.read_register(address=999, unit_id=40)


class TestHttpClientScenes:
    """Test scene functionality."""

    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance."""
        return KermiHttpClient(host="192.168.1.100")

    @pytest.mark.asyncio
    async def test_get_scenes(self, http_client):
        """Test getting all scenes."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [
                {
                    "SceneId": "scene-1",
                    "DisplayName": "Heizen Tag",
                    "Description": "Day heating schedule",
                    "Priority": 7,
                    "Enabled": True,
                    "LastUpdateUtc": "2024-06-29T14:45:24Z",
                },
                {
                    "SceneId": "scene-2",
                    "DisplayName": "Nacht Modus",
                    "Description": None,
                    "Priority": 10,
                    "Enabled": False,
                    "LastUpdateUtc": "2024-07-01T10:00:00Z",
                },
            ]

            scenes = await http_client.get_scenes()

            mock_request.assert_called_once_with(
                "Scene/GetScenesByDeviceId",
                {"DeviceId": "00000000-0000-0000-0000-000000000000"},
            )
            assert len(scenes) == 2
            assert isinstance(scenes[0], SceneOverview)
            assert scenes[0].scene_id == "scene-1"
            assert scenes[0].display_name == "Heizen Tag"
            assert scenes[0].enabled is True
            assert scenes[1].enabled is False

    @pytest.mark.asyncio
    async def test_get_scenes_empty(self, http_client):
        """Test getting scenes when none exist."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = []

            scenes = await http_client.get_scenes()

            assert scenes == []

    @pytest.mark.asyncio
    async def test_get_scene_by_id(self, http_client):
        """Test getting a full scene by ID."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "SceneId": "scene-1",
                "DisplayName": "Heizen Tag",
                "Description": "Day heating",
                "Priority": 7,
                "Enabled": True,
                "LastUpdateUtc": "2024-06-29T14:45:24Z",
                "ConditionTreeData": {
                    "Id": "condition-1",
                    "Enabled": True,
                    "ConditionsAndData": [],
                },
                "ActionDataForSerialization": [
                    {
                        "Data": {
                            "$type": "BMS.Shared.SceneData.Actions.SceneDataActionSetDatapoints",
                            "Enabled": True,
                        }
                    }
                ],
            }

            scene = await http_client.get_scene("scene-1")

            mock_request.assert_called_once_with(
                "Scene/GetSceneById",
                {"SceneId": "scene-1"},
            )
            assert isinstance(scene, Scene)
            assert scene.scene_id == "scene-1"
            assert scene.display_name == "Heizen Tag"
            assert scene.condition_tree_data["Id"] == "condition-1"
            assert len(scene.action_data) == 1

    @pytest.mark.asyncio
    async def test_get_scene_not_found(self, http_client):
        """Test getting a scene that doesn't exist."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None

            with pytest.raises(HttpError, match="Scene scene-999 not found"):
                await http_client.get_scene("scene-999")

    @pytest.mark.asyncio
    async def test_get_scene_state(self, http_client):
        """Test getting scene execution state."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "SceneId": "scene-1",
                "DisplayName": "Heizen Tag",
                "SceneState": {
                    "ConditionIsTrue": True,
                    "ActionIsRunning": False,
                    "LastConditionCheckUtc": "2024-07-15T12:00:00Z",
                    "ExecutionTimeMs": 150,
                },
            }

            state = await http_client.get_scene_state("scene-1")

            mock_request.assert_called_once_with(
                "Scene/GetSceneOverviewById",
                {"SceneId": "scene-1"},
            )
            assert isinstance(state, SceneState)
            assert state.condition_is_true is True
            assert state.action_is_running is False
            assert state.execution_time_ms == 150

    @pytest.mark.asyncio
    async def test_get_scene_state_not_found(self, http_client):
        """Test getting state for non-existent scene."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None

            with pytest.raises(HttpError, match="Scene scene-999 not found"):
                await http_client.get_scene_state("scene-999")

    @pytest.mark.asyncio
    async def test_execute_scene(self, http_client):
        """Test executing a scene."""
        with patch.object(http_client._session, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"StatusCode": 0}

            await http_client.execute_scene("scene-1")

            mock_request.assert_called_once_with(
                "Scene/ExecuteScene",
                {"SceneId": "scene-1"},
            )
