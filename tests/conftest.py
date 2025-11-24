"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from kermi_xcenter import KermiModbusClient


@pytest.fixture
def mock_modbus_response():
    """Create a mock Modbus response."""

    def _create_response(registers=None, is_error=False):
        response = MagicMock()
        response.isError.return_value = is_error
        if registers is not None:
            response.registers = registers
        return response

    return _create_response


@pytest.fixture
def mock_tcp_client():
    """Create a mock TCP Modbus client."""
    client = AsyncMock()
    client.connected = True
    return client


@pytest.fixture
async def kermi_client(mock_tcp_client, monkeypatch):
    """Create a KermiModbusClient with mocked pymodbus client."""
    # Mock the AsyncModbusTcpClient
    monkeypatch.setattr(
        "kermi_xcenter.client.AsyncModbusTcpClient", lambda **_kwargs: mock_tcp_client
    )

    client = KermiModbusClient(host="192.168.1.100", port=502)
    await client.connect()

    yield client

    await client.disconnect()


@pytest.fixture
def sample_register_values():
    """Sample register values for testing."""
    return {
        # Temperature (in 0.1°C units)
        "temp_235": 235,  # 23.5°C
        "temp_minus_50": -50,  # -5.0°C
        # Power (in 0.01 kW units)
        "power_315": 315,  # 3.15 kW
        "power_1250": 1250,  # 12.50 kW
        # COP (in 0.01 units)
        "cop_425": 425,  # 4.25
        "cop_350": 350,  # 3.50
        # Flow rate (in 0.1 l/min units)
        "flow_125": 125,  # 12.5 l/min
        # Enums
        "status_heating": 4,  # HeatPumpStatus.HEATING
        "status_standby": 0,  # HeatPumpStatus.STANDBY
        # Boolean
        "bool_true": 1,
        "bool_false": 0,
        # Operating hours
        "hours_1000": 1000,
    }
