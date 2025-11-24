"""Tests for KermiModbusClient."""

import sys

import pytest

from kermi_xcenter import KermiModbusClient
from kermi_xcenter.exceptions import ConnectionError, RegisterReadError, RegisterWriteError


class TestClientConnection:
    """Test client connection management."""

    @pytest.mark.asyncio
    async def test_tcp_client_creation(self):
        """Test TCP client is created with correct parameters."""
        client = KermiModbusClient(host="192.168.1.100", port=502, timeout=5.0)
        assert client._timeout == 5.0
        assert not client._use_rtu

    @pytest.mark.skipif("serial" not in sys.modules, reason="pyserial not installed")
    def test_rtu_client_creation(self):
        """Test RTU client is created with correct parameters."""
        client = KermiModbusClient(
            port="/dev/ttyUSB0",
            baudrate=9600,
            use_rtu=True,
        )
        assert client._use_rtu

    def test_tcp_without_host_raises_error(self):
        """Test that TCP connection without host raises ValueError."""
        with pytest.raises(ValueError, match="Host must be provided"):
            KermiModbusClient(port=502, use_rtu=False)

    @pytest.mark.asyncio
    async def test_connect_success(self, kermi_client):
        """Test successful connection."""
        assert kermi_client.is_connected

    @pytest.mark.asyncio
    async def test_disconnect(self, kermi_client):
        """Test disconnection."""
        await kermi_client.disconnect()
        assert not kermi_client._connected

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_tcp_client, monkeypatch):
        """Test async context manager usage."""
        monkeypatch.setattr(
            "kermi_xcenter.client.AsyncModbusTcpClient", lambda **_kwargs: mock_tcp_client
        )

        client = KermiModbusClient(host="192.168.1.100")

        async with client:
            assert client.is_connected

        assert not client._connected


class TestClientReadOperations:
    """Test client read operations."""

    @pytest.mark.asyncio
    async def test_read_single_register(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading a single register."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([235])

        value = await kermi_client.read_register(address=1, unit_id=40)

        assert value == 235
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=1, count=1, device_id=40
        )

    @pytest.mark.asyncio
    async def test_read_multiple_registers(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test reading multiple registers."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([235, 315, 425])

        values = await kermi_client.read_register(address=1, unit_id=40, count=3)

        assert values == [235, 315, 425]
        mock_tcp_client.read_holding_registers.assert_called_once_with(
            address=1, count=3, device_id=40
        )

    @pytest.mark.asyncio
    async def test_read_register_error(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading register with error response."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response(is_error=True)

        with pytest.raises(RegisterReadError):
            await kermi_client.read_register(address=1, unit_id=40)

    @pytest.mark.asyncio
    async def test_read_when_not_connected(self):
        """Test reading when not connected raises error."""
        client = KermiModbusClient(host="192.168.1.100")

        with pytest.raises(ConnectionError, match="Not connected"):
            await client.read_register(address=1, unit_id=40)


class TestClientWriteOperations:
    """Test client write operations."""

    @pytest.mark.asyncio
    async def test_write_single_register(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test writing a single register."""
        mock_tcp_client.write_register.return_value = mock_modbus_response()

        await kermi_client.write_register(address=301, value=2000, unit_id=40)

        mock_tcp_client.write_register.assert_called_once_with(
            address=301, value=2000, device_id=40
        )

    @pytest.mark.asyncio
    async def test_write_register_error(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test writing register with error response."""
        mock_tcp_client.write_register.return_value = mock_modbus_response(is_error=True)

        with pytest.raises(RegisterWriteError):
            await kermi_client.write_register(address=301, value=2000, unit_id=40)

    @pytest.mark.asyncio
    async def test_write_multiple_registers(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test writing multiple registers."""
        mock_tcp_client.write_registers.return_value = mock_modbus_response()

        await kermi_client.write_registers(address=300, values=[2000, 235, 520], unit_id=40)

        mock_tcp_client.write_registers.assert_called_once_with(
            address=300, values=[2000, 235, 520], device_id=40
        )

    @pytest.mark.asyncio
    async def test_write_when_not_connected(self):
        """Test writing when not connected raises error."""
        client = KermiModbusClient(host="192.168.1.100")

        with pytest.raises(ConnectionError, match="Not connected"):
            await client.write_register(address=301, value=2000, unit_id=40)


class TestClientRetryLogic:
    """Test client retry logic."""

    @pytest.mark.asyncio
    async def test_read_retry_on_exception(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test that read retries on exception."""
        # First call fails, second succeeds
        mock_tcp_client.read_holding_registers.side_effect = [
            Exception("Network error"),
            mock_modbus_response([235]),
        ]

        value = await kermi_client.read_register(address=1, unit_id=40)

        assert value == 235
        assert mock_tcp_client.read_holding_registers.call_count == 2

    @pytest.mark.asyncio
    async def test_write_retry_on_exception(
        self, kermi_client, mock_tcp_client, mock_modbus_response
    ):
        """Test that write retries on exception."""
        # First call fails, second succeeds
        mock_tcp_client.write_register.side_effect = [
            Exception("Network error"),
            mock_modbus_response(),
        ]

        await kermi_client.write_register(address=301, value=2000, unit_id=40)

        assert mock_tcp_client.write_register.call_count == 2

    @pytest.mark.asyncio
    async def test_read_max_retries_exceeded(self, kermi_client, mock_tcp_client):
        """Test that max retries causes failure."""
        mock_tcp_client.read_holding_registers.side_effect = Exception("Network error")

        with pytest.raises(RegisterReadError, match="Max retries exceeded"):
            await kermi_client.read_register(address=1, unit_id=40)
