"""Tests for UniversalModule device."""

import pytest

from kermi_xcenter import UniversalModule
from kermi_xcenter.types import EnergyMode, HeatingCircuitStatus, OperatingMode, OperatingType


class TestUniversalModuleHeatingCircuit:
    """Test universal module heating circuit."""

    @pytest.mark.asyncio
    async def test_get_heating_circuit_status(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading heating circuit status."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([2])

        universal = UniversalModule(kermi_client)
        status = await universal.get_heating_circuit_status()

        assert status == HeatingCircuitStatus.COOLING
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=150, count=1, device_id=30
        )

    @pytest.mark.asyncio
    async def test_get_heating_circuit_actual(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading actual temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([215])

        universal = UniversalModule(kermi_client)
        temp = await universal.get_heating_circuit_actual()

        assert temp == 21.5

    @pytest.mark.asyncio
    async def test_get_heating_circuit_setpoint(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading setpoint temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([225])

        universal = UniversalModule(kermi_client)
        temp = await universal.get_heating_circuit_setpoint()

        assert temp == 22.5


class TestUniversalModuleOperatingModes:
    """Test operating mode control."""

    @pytest.mark.asyncio
    async def test_get_operating_mode(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading operating mode."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([1])

        universal = UniversalModule(kermi_client)
        mode = await universal.get_operating_mode()

        assert mode == OperatingMode.HEATING

    @pytest.mark.asyncio
    async def test_get_operating_type(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading operating type."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([0])

        universal = UniversalModule(kermi_client)
        op_type = await universal.get_operating_type()

        assert op_type == OperatingType.AUTO

    @pytest.mark.asyncio
    async def test_set_operating_type(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test setting operating type."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        universal = UniversalModule(kermi_client)
        await universal.set_operating_type(OperatingType.AUTO)

        mock_tcp_client.write_register.assert_called_once_with(address=154, value=0, device_id=30)


class TestUniversalModuleEnergyMode:
    """Test energy mode control."""

    @pytest.mark.asyncio
    async def test_get_energy_mode(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading energy mode."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([2])

        universal = UniversalModule(kermi_client)
        mode = await universal.get_energy_mode()

        assert mode == EnergyMode.NORMAL

    @pytest.mark.asyncio
    async def test_set_energy_mode_eco(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test setting energy mode to ECO."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        universal = UniversalModule(kermi_client)
        await universal.set_energy_mode(EnergyMode.ECO)

        mock_tcp_client.write_register.assert_called_once_with(address=155, value=1, device_id=30)

    @pytest.mark.asyncio
    async def test_set_energy_mode_comfort(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting energy mode to COMFORT."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        universal = UniversalModule(kermi_client)
        await universal.set_energy_mode(EnergyMode.COMFORT)

        mock_tcp_client.write_register.assert_called_once_with(address=155, value=3, device_id=30)


class TestUniversalModuleHeatingCurve:
    """Test heating curve control."""

    @pytest.mark.asyncio
    async def test_get_heating_curve_parallel_offset(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading heating curve offset."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([15])

        universal = UniversalModule(kermi_client)
        offset = await universal.get_heating_curve_parallel_offset()

        assert offset == 1.5

    @pytest.mark.asyncio
    async def test_set_heating_curve_parallel_offset(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting heating curve offset."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        universal = UniversalModule(kermi_client)
        await universal.set_heating_curve_parallel_offset(-2.0)

        mock_tcp_client.write_register.assert_called_once_with(address=156, value=-20, device_id=30)


class TestUniversalModuleTemperatureSensors:
    """Test temperature sensor readings."""

    @pytest.mark.asyncio
    async def test_get_t1_temperature(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading T1 sensor."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([235])

        universal = UniversalModule(kermi_client)
        temp = await universal.get_t1_temperature()

        assert temp == 23.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=250, count=1, device_id=30
        )

    @pytest.mark.asyncio
    async def test_get_t4_temperature(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading T4 sensor."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([195])

        universal = UniversalModule(kermi_client)
        temp = await universal.get_t4_temperature()

        assert temp == 19.5


class TestUniversalModuleSeasonThresholds:
    """Test season threshold settings."""

    @pytest.mark.asyncio
    async def test_set_cooling_mode_on(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test setting cooling mode on threshold."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        universal = UniversalModule(kermi_client)
        await universal.set_cooling_mode_on(24.0)

        mock_tcp_client.write_register.assert_called_once_with(address=160, value=240, device_id=30)

    @pytest.mark.asyncio
    async def test_get_summer_mode_active(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading summer mode active status."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([1])

        universal = UniversalModule(kermi_client)
        active = await universal.get_summer_mode_active()

        assert active is True
