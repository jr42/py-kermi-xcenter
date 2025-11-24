"""Tests for exception handling."""

import pytest

from kermi_xcenter.exceptions import (
    ConnectionError,
    KermiModbusError,
    ReadOnlyRegisterError,
    RegisterReadError,
    RegisterWriteError,
    ValidationError,
)
from kermi_xcenter.models.base import KermiDevice
from kermi_xcenter.registers import HEAT_PUMP_REGISTERS


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_base_exception(self):
        """Test base exception."""
        exc = KermiModbusError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_connection_error(self):
        """Test connection error."""
        exc = ConnectionError("Connection failed")
        assert isinstance(exc, KermiModbusError)

    def test_register_read_error(self):
        """Test register read error."""
        exc = RegisterReadError(address=100, message="Read failed")
        assert exc.address == 100
        assert "100" in str(exc)
        assert isinstance(exc, KermiModbusError)

    def test_register_write_error(self):
        """Test register write error."""
        exc = RegisterWriteError(address=200, value=1500, message="Write failed")
        assert exc.address == 200
        assert exc.value == 1500
        assert "200" in str(exc)
        assert "1500" in str(exc)

    def test_validation_error(self):
        """Test validation error."""
        exc = ValidationError(field="temperature", value=100.0, message="Too high")
        assert exc.field == "temperature"
        assert exc.value == 100.0
        assert "temperature" in str(exc)

    def test_read_only_register_error(self):
        """Test read-only register error."""
        exc = ReadOnlyRegisterError(register_name="outdoor_temperature")
        assert exc.register_name == "outdoor_temperature"
        assert "read-only" in str(exc)


class TestValidationInDeviceClass:
    """Test validation in device class."""

    @pytest.mark.asyncio
    async def test_write_to_readonly_register(self, kermi_client):
        """Test that writing to read-only register raises error."""
        device = KermiDevice(kermi_client, unit_id=40, registers=HEAT_PUMP_REGISTERS)

        # outdoor_temperature is read-only
        readonly_register = HEAT_PUMP_REGISTERS["outdoor_temperature"]

        with pytest.raises(ReadOnlyRegisterError):
            await device._write_register(readonly_register, 25.0)

    @pytest.mark.asyncio
    async def test_write_value_below_min(self, kermi_client):
        """Test that writing value below minimum raises error."""
        device = KermiDevice(kermi_client, unit_id=40, registers=HEAT_PUMP_REGISTERS)

        # pv_modulation_setpoint_heating has no explicit min in our current setup,
        # but let's test with a register that has limits
        # For this test, we'll use a mock register with limits
        from kermi_xcenter.registers import RegisterDef
        from kermi_xcenter.utils.conversions import raw_to_temperature, temperature_to_raw

        test_register = RegisterDef(
            address=999,
            name="test_temp",
            german_name="test",
            description="Test",
            unit="°C",
            attribute="R/W",
            min_value=0.0,
            max_value=50.0,
            converter=raw_to_temperature,
            inverse_converter=temperature_to_raw,
        )

        with pytest.raises(ValidationError, match="below minimum"):
            await device._write_register(test_register, -10.0)

    @pytest.mark.asyncio
    async def test_write_value_above_max(self, kermi_client):
        """Test that writing value above maximum raises error."""
        device = KermiDevice(kermi_client, unit_id=40, registers=HEAT_PUMP_REGISTERS)

        from kermi_xcenter.registers import RegisterDef
        from kermi_xcenter.utils.conversions import raw_to_temperature, temperature_to_raw

        test_register = RegisterDef(
            address=999,
            name="test_temp",
            german_name="test",
            description="Test",
            unit="°C",
            attribute="R/W",
            min_value=0.0,
            max_value=50.0,
            converter=raw_to_temperature,
            inverse_converter=temperature_to_raw,
        )

        with pytest.raises(ValidationError, match="above maximum"):
            await device._write_register(test_register, 100.0)
