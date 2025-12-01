"""Tests for data conversion utilities."""

import pytest

from kermi_xcenter.utils.conversions import (
    raw_to_cop,
    raw_to_flow_rate,
    raw_to_power,
    raw_to_temperature,
    temperature_to_raw,
)


class TestTemperatureConversions:
    """Test temperature conversion functions."""

    def test_raw_to_temperature_positive(self):
        """Test conversion of positive temperature."""
        assert raw_to_temperature(235) == 23.5
        assert raw_to_temperature(100) == 10.0
        assert raw_to_temperature(0) == 0.0

    def test_raw_to_temperature_negative(self):
        """Test conversion of negative temperature."""
        assert raw_to_temperature(-50) == -5.0
        assert raw_to_temperature(-100) == -10.0

    def test_temperature_to_raw_positive(self):
        """Test conversion to raw temperature value."""
        assert temperature_to_raw(23.5) == 235
        assert temperature_to_raw(10.0) == 100
        assert temperature_to_raw(0.0) == 0

    def test_temperature_to_raw_negative(self):
        """Test conversion to raw temperature value (negative)."""
        assert temperature_to_raw(-5.0) == -50
        assert temperature_to_raw(-10.0) == -100

    def test_temperature_roundtrip(self):
        """Test temperature conversion roundtrip."""
        temps = [23.5, -5.0, 0.0, 50.5, -15.3]
        for temp in temps:
            raw = temperature_to_raw(temp)
            converted = raw_to_temperature(raw)
            assert converted == pytest.approx(temp, abs=0.1)


class TestPowerConversions:
    """Test power conversion functions."""

    def test_raw_to_power_small(self):
        """Test conversion of small power values."""
        assert raw_to_power(71) == 7.1
        assert raw_to_power(10) == 1.0

    def test_raw_to_power_large(self):
        """Test conversion of large power values."""
        assert raw_to_power(125) == 12.5
        assert raw_to_power(500) == 50.0

    def test_raw_to_power_zero(self):
        """Test conversion of zero power."""
        assert raw_to_power(0) == 0.0


class TestCOPConversions:
    """Test COP conversion functions."""

    def test_raw_to_cop_typical(self):
        """Test conversion of typical COP values."""
        assert raw_to_cop(39) == 3.9
        assert raw_to_cop(45) == 4.5
        assert raw_to_cop(50) == 5.0

    def test_raw_to_cop_low(self):
        """Test conversion of low COP values."""
        assert raw_to_cop(10) == 1.0
        assert raw_to_cop(5) == 0.5


class TestFlowRateConversions:
    """Test flow rate conversion functions."""

    def test_raw_to_flow_rate(self):
        """Test conversion of flow rate values."""
        assert raw_to_flow_rate(125) == 12.5
        assert raw_to_flow_rate(50) == 5.0
        assert raw_to_flow_rate(0) == 0.0
        assert raw_to_flow_rate(1000) == 100.0
