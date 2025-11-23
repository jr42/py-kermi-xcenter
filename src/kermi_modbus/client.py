"""Async Modbus client for Kermi heat pump communication.

This module provides an async wrapper around pymodbus for communicating
with Kermi heat pump devices over Modbus TCP or RTU.
"""

import asyncio
import logging
from typing import Self

from pymodbus.client import AsyncModbusTcpClient, AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

from .exceptions import ConnectionError, RegisterReadError, RegisterWriteError
from .types import ModbusAddress, RegisterValue, UnitId

logger = logging.getLogger(__name__)


class KermiModbusClient:
    """Async Modbus client for Kermi heat pump systems.

    Supports both TCP and RTU connections with automatic connection management.

    Examples:
        TCP connection:
        >>> client = KermiModbusClient(host="192.168.1.100", port=502)
        >>> async with client:
        ...     value = await client.read_register(1, unit_id=40)

        RTU connection:
        >>> client = KermiModbusClient(
        ...     port="/dev/ttyUSB0",
        ...     baudrate=9600,
        ...     use_rtu=True
        ... )
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | str = 502,
        timeout: float = 3.0,
        retry_on_empty: bool = True,
        retries: int = 3,
        use_rtu: bool = False,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: int = 1,
    ) -> None:
        """Initialize the Modbus client.

        Args:
            host: IP address or hostname for TCP connection (required if not RTU)
            port: TCP port number (default: 502) or serial port path for RTU (e.g., "/dev/ttyUSB0")
            timeout: Connection timeout in seconds (default: 3.0)
            retry_on_empty: Retry if response is empty (default: True)
            retries: Number of retry attempts (default: 3)
            use_rtu: Use RTU serial connection instead of TCP (default: False)
            baudrate: Serial baudrate for RTU (default: 9600)
            bytesize: Serial bytesize for RTU (default: 8)
            parity: Serial parity for RTU (default: "N")
            stopbits: Serial stopbits for RTU (default: 1)

        Raises:
            ValueError: If TCP is used but no host is provided
        """
        self._use_rtu = use_rtu
        self._timeout = timeout
        self._retry_on_empty = retry_on_empty
        self._retries = retries

        if use_rtu:
            logger.info(f"Configuring RTU client on {port} at {baudrate} baud")
            self._client: AsyncModbusTcpClient | AsyncModbusSerialClient = AsyncModbusSerialClient(
                port=str(port),
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
            )
        else:
            if host is None:
                raise ValueError("Host must be provided for TCP connection")
            logger.info(f"Configuring TCP client for {host}:{port}")
            self._client = AsyncModbusTcpClient(
                host=host,
                port=int(port),
                timeout=timeout,
            )

        self._connected = False

    async def connect(self) -> None:
        """Establish connection to the Modbus device.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info("Connecting to Modbus device...")
            await self._client.connect()
            self._connected = True
            logger.info("Connected successfully")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def disconnect(self) -> None:
        """Close connection to the Modbus device."""
        if self._connected:
            logger.info("Disconnecting from Modbus device...")
            self._client.close()
            self._connected = False
            logger.info("Disconnected")

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client.connected

    async def read_register(
        self,
        address: ModbusAddress,
        unit_id: UnitId,
        count: int = 1,
    ) -> RegisterValue | list[RegisterValue]:
        """Read one or more holding registers.

        Args:
            address: Register address to read
            unit_id: Modbus unit/slave ID
            count: Number of registers to read (default: 1)

        Returns:
            Single register value if count=1, otherwise list of values

        Raises:
            RegisterReadError: If read operation fails
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Modbus device")

        for attempt in range(self._retries):
            try:
                logger.debug(f"Reading register {address} (unit {unit_id}, count {count}), attempt {attempt + 1}")
                response = await self._client.read_holding_registers(
                    address=address,
                    count=count,
                    slave=unit_id,
                )

                if response.isError():
                    raise RegisterReadError(address, f"Modbus error: {response}")

                if hasattr(response, "registers"):
                    values = response.registers
                    if count == 1:
                        return values[0]
                    return values
                else:
                    raise RegisterReadError(address, "Invalid response format")

            except ModbusException as e:
                if attempt < self._retries - 1:
                    logger.warning(f"Read failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                raise RegisterReadError(address, str(e)) from e

        raise RegisterReadError(address, "Max retries exceeded")

    async def write_register(
        self,
        address: ModbusAddress,
        value: RegisterValue,
        unit_id: UnitId,
    ) -> None:
        """Write a single holding register.

        Args:
            address: Register address to write
            value: Value to write (16-bit integer)
            unit_id: Modbus unit/slave ID

        Raises:
            RegisterWriteError: If write operation fails
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Modbus device")

        for attempt in range(self._retries):
            try:
                logger.debug(f"Writing {value} to register {address} (unit {unit_id}), attempt {attempt + 1}")
                response = await self._client.write_register(
                    address=address,
                    value=value,
                    slave=unit_id,
                )

                if response.isError():
                    raise RegisterWriteError(address, value, f"Modbus error: {response}")

                logger.debug(f"Successfully wrote {value} to register {address}")
                return

            except ModbusException as e:
                if attempt < self._retries - 1:
                    logger.warning(f"Write failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                raise RegisterWriteError(address, value, str(e)) from e

        raise RegisterWriteError(address, value, "Max retries exceeded")

    async def write_registers(
        self,
        address: ModbusAddress,
        values: list[RegisterValue],
        unit_id: UnitId,
    ) -> None:
        """Write multiple holding registers.

        Args:
            address: Starting register address
            values: List of values to write
            unit_id: Modbus unit/slave ID

        Raises:
            RegisterWriteError: If write operation fails
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Modbus device")

        for attempt in range(self._retries):
            try:
                logger.debug(f"Writing {len(values)} registers starting at {address} (unit {unit_id})")
                response = await self._client.write_registers(
                    address=address,
                    values=values,
                    slave=unit_id,
                )

                if response.isError():
                    raise RegisterWriteError(address, values[0] if values else 0, f"Modbus error: {response}")

                logger.debug(f"Successfully wrote {len(values)} registers")
                return

            except ModbusException as e:
                if attempt < self._retries - 1:
                    logger.warning(f"Write failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                raise RegisterWriteError(address, values[0] if values else 0, str(e)) from e

        raise RegisterWriteError(address, values[0] if values else 0, "Max retries exceeded")
