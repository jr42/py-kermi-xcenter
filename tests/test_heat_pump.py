"""Tests for HeatPump device."""

import pytest

from kermi_xcenter import HeatPump, HeatPumpStatus


class TestHeatPumpTemperatures:
    """Test heat pump temperature readings."""

    @pytest.mark.asyncio
    async def test_get_outdoor_temperature(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading outdoor temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([235])

        heat_pump = HeatPump(kermi_client)
        temp = await heat_pump.get_outdoor_temperature()

        assert temp == 23.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=3, count=1, device_id=40
        )

    @pytest.mark.asyncio
    async def test_get_supply_temp(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading supply temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([525])

        heat_pump = HeatPump(kermi_client)
        temp = await heat_pump.get_supply_temp_heat_pump()

        assert temp == 52.5

    @pytest.mark.asyncio
    async def test_get_negative_temperature(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading negative temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([-50])

        heat_pump = HeatPump(kermi_client)
        temp = await heat_pump.get_outdoor_temperature()

        assert temp == -5.0


class TestHeatPumpCOP:
    """Test heat pump COP readings."""

    @pytest.mark.asyncio
    async def test_get_cop_total(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading total COP."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([39])

        heat_pump = HeatPump(kermi_client)
        cop = await heat_pump.get_cop_total()

        assert cop == 3.9
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=100, count=1, device_id=40
        )

    @pytest.mark.asyncio
    async def test_get_cop_heating(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading heating COP."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([35])

        heat_pump = HeatPump(kermi_client)
        cop = await heat_pump.get_cop_heating()

        assert cop == 3.5


class TestHeatPumpPower:
    """Test heat pump power readings."""

    @pytest.mark.asyncio
    async def test_get_power_total(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading total power."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([125])

        heat_pump = HeatPump(kermi_client)
        power = await heat_pump.get_power_total()

        assert power == 12.5
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=104, count=1, device_id=40
        )

    @pytest.mark.asyncio
    async def test_get_power_electrical(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading electrical power."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([31])

        heat_pump = HeatPump(kermi_client)
        power = await heat_pump.get_power_electrical_total()

        assert power == 3.1


class TestHeatPumpStatus:
    """Test heat pump status readings."""

    @pytest.mark.asyncio
    async def test_get_heat_pump_status_heating(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading heat pump status as HEATING."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([4])

        heat_pump = HeatPump(kermi_client)
        status = await heat_pump.get_heat_pump_status()

        assert status == HeatPumpStatus.HEATING
        assert status.name == "HEATING"

    @pytest.mark.asyncio
    async def test_get_heat_pump_status_standby(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading heat pump status as STANDBY."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([0])

        heat_pump = HeatPump(kermi_client)
        status = await heat_pump.get_heat_pump_status()

        assert status == HeatPumpStatus.STANDBY

    @pytest.mark.asyncio
    async def test_get_global_alarm(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading global alarm status."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([1])

        heat_pump = HeatPump(kermi_client)
        alarm = await heat_pump.get_global_alarm()

        assert alarm is True


class TestHeatPumpPVModulation:
    """Test heat pump PV modulation control."""

    @pytest.mark.asyncio
    async def test_get_pv_modulation_power(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading PV modulation power."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([2000])

        heat_pump = HeatPump(kermi_client)
        power = await heat_pump.get_pv_modulation_power()

        assert power == 2000

    @pytest.mark.asyncio
    async def test_set_pv_modulation_power(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting PV modulation power."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        heat_pump = HeatPump(kermi_client)
        await heat_pump.set_pv_modulation_power(2500)

        mock_tcp_client.write_register.assert_called_once_with(
            address=301, value=2500, device_id=40
        )

    @pytest.mark.asyncio
    async def test_set_pv_modulation_setpoint_heating(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test setting PV modulation heating setpoint."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        heat_pump = HeatPump(kermi_client)
        await heat_pump.set_pv_modulation_setpoint_heating(23.5)

        # Should convert 23.5°C to raw value 235
        mock_tcp_client.write_register.assert_called_once_with(address=302, value=235, device_id=40)


class TestHeatPumpOperatingHours:
    """Test heat pump operating hours."""

    @pytest.mark.asyncio
    async def test_get_operating_hours_compressor(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading compressor operating hours."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([5432])

        heat_pump = HeatPump(kermi_client)
        hours = await heat_pump.get_operating_hours_compressor()

        assert hours == 5432
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=152, count=1, device_id=40
        )


class TestHeatPumpFlowRate:
    """Test heat pump flow rate."""

    @pytest.mark.asyncio
    async def test_get_flow_rate(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading flow rate."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([125])

        heat_pump = HeatPump(kermi_client)
        flow = await heat_pump.get_flow_rate_heat_pump()

        assert flow == 12.5
