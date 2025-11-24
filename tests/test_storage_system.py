"""Tests for StorageSystem device."""

import pytest

from kermi_xcenter import StorageSystem
from kermi_xcenter.types import (
    EnergyMode,
    HeatingCircuitStatus,
    OperatingMode,
    SeasonSelection,
)


class TestStorageSystemTemperatures:
    """Test storage system temperature readings."""

    @pytest.mark.asyncio
    async def test_get_heating_actual(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading heating actual temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([455])

        storage = StorageSystem(kermi_client, unit_id=50)
        temp = await storage.get_heating_actual()

        assert temp == 45.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=1, count=1, device_id=50
        )

    @pytest.mark.asyncio
    async def test_get_hot_water_actual(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading hot water actual temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([505])

        storage = StorageSystem(kermi_client, unit_id=51)
        temp = await storage.get_hot_water_actual()

        assert temp == 50.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=100, count=1, device_id=51
        )


class TestStorageSystemHotWaterControl:
    """Test hot water control."""

    @pytest.mark.asyncio
    async def test_get_hot_water_setpoint_constant(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading hot water constant setpoint."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([480])

        storage = StorageSystem(kermi_client, unit_id=51)
        temp = await storage.get_hot_water_setpoint_constant()

        assert temp == 48.0

    @pytest.mark.asyncio
    async def test_set_hot_water_setpoint_constant(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting hot water constant setpoint."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=51)
        await storage.set_hot_water_setpoint_constant(52.5)

        # Should convert 52.5°C to raw value 525
        mock_tcp_client.write_register.assert_called_once_with(address=102, value=525, device_id=51)

    @pytest.mark.asyncio
    async def test_set_hot_water_single_charge_active(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test activating single charge."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=51)
        await storage.set_hot_water_single_charge_active(True)

        mock_tcp_client.write_register.assert_called_once_with(address=103, value=1, device_id=51)

    @pytest.mark.asyncio
    async def test_set_hot_water_single_charge_setpoint(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting single charge setpoint."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=51)
        await storage.set_hot_water_single_charge_setpoint(55.0)

        mock_tcp_client.write_register.assert_called_once_with(address=104, value=550, device_id=51)


class TestStorageSystemHeatingCircuit:
    """Test heating circuit control."""

    @pytest.mark.asyncio
    async def test_get_heating_circuit_status(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading heating circuit status."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([1])

        storage = StorageSystem(kermi_client, unit_id=50)
        status = await storage.get_heating_circuit_status()

        assert status == HeatingCircuitStatus.HEATING
        assert status.name == "HEATING"

    @pytest.mark.asyncio
    async def test_get_heating_circuit_operating_mode(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading operating mode."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([1])

        storage = StorageSystem(kermi_client, unit_id=50)
        mode = await storage.get_heating_circuit_operating_mode()

        assert mode == OperatingMode.HEATING

    @pytest.mark.asyncio
    async def test_set_heating_circuit_energy_mode(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting energy mode."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=50)
        await storage.set_heating_circuit_energy_mode(EnergyMode.ECO)

        mock_tcp_client.write_register.assert_called_once_with(
            address=155, value=1, device_id=50  # ECO = 1
        )

    @pytest.mark.asyncio
    async def test_set_heating_curve_parallel_offset(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting heating curve offset."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=50)
        await storage.set_heating_curve_parallel_offset(2.5)

        mock_tcp_client.write_register.assert_called_once_with(address=156, value=25, device_id=50)


class TestStorageSystemSeasonControl:
    """Test season control."""

    @pytest.mark.asyncio
    async def test_get_season_selection_manual(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading season selection."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([0])

        storage = StorageSystem(kermi_client, unit_id=50)
        season = await storage.get_season_selection_manual()

        assert season == SeasonSelection.AUTO

    @pytest.mark.asyncio
    async def test_set_season_selection_manual(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting season selection."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=50)
        await storage.set_season_selection_manual(SeasonSelection.HEATING)

        mock_tcp_client.write_register.assert_called_once_with(address=157, value=1, device_id=50)

    @pytest.mark.asyncio
    async def test_set_summer_mode_heating_off(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting summer mode threshold."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        storage = StorageSystem(kermi_client, unit_id=50)
        await storage.set_summer_mode_heating_off(20.0)

        mock_tcp_client.write_register.assert_called_once_with(address=158, value=200, device_id=50)


class TestStorageSystemTemperatureSensors:
    """Test temperature sensor readings."""

    @pytest.mark.asyncio
    async def test_get_outdoor_temperature(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading outdoor temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([185])

        storage = StorageSystem(kermi_client, unit_id=50)
        temp = await storage.get_outdoor_temperature()

        assert temp == 18.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=254, count=1, device_id=50
        )

    @pytest.mark.asyncio
    async def test_get_t1_temperature(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading T1 sensor."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([225])

        storage = StorageSystem(kermi_client, unit_id=50)
        temp = await storage.get_t1_temperature()

        assert temp == 22.5


class TestStorageSystemOperatingHours:
    """Test operating hours."""

    @pytest.mark.asyncio
    async def test_get_operating_hours_circuit_pump(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading circuit pump operating hours."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([3456])

        storage = StorageSystem(kermi_client, unit_id=50)
        hours = await storage.get_operating_hours_circuit_pump()

        assert hours == 3456
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=300, count=1, device_id=50
        )
