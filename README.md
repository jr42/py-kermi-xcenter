# Kermi x-center Python Interface

Async Python interface for Kermi heat pumps via x-center module. Supports both **HTTP API** (recommended) and **Modbus TCP/RTU**.

[![CI](https://github.com/jr42/py-kermi-xcenter/workflows/CI/badge.svg)](https://github.com/jr42/py-kermi-xcenter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jr42/py-kermi-xcenter/branch/main/graph/badge.svg)](https://codecov.io/gh/jr42/py-kermi-xcenter)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Transport Options

| Feature | HTTP API | Modbus |
|---------|----------|--------|
| **API Status** | Unofficial/Undocumented | Official (Kermi docs) |
| **Setup Required** | None | Kermi support activation |
| **Datapoints** | 250+ (all available) | ~90 (documented subset) |
| **Efficiency** | 2 API calls for all data | ~30 register reads |
| **Device Discovery** | Automatic | Manual configuration |
| **Alarms** | Current + History | Not available |
| **IFM Access** | Full (SmartGrid, I/O, S0) | Not available |

**Recommendation:** Use HTTP for most use cases. Use Modbus only if HTTP is unavailable or you need real-time polling at high frequency.

## Requirements

### Hardware Compatibility

This library is tested with:
- **x-center IFM**: Firmware version 1.6.3.42
- **Heat pump**: x-change dynamic pro ac 6 AW E (air/water heat pump)
- **Buffer system**: x-buffer combi pro (Puffersystemmodul)

Other Kermi heat pump models with x-center module should also work.

### Modbus Activation (Modbus only)

**IMPORTANT**: Modbus must be activated on your x-center module before use.

Contact Kermi support to enable Modbus communication. For technical details, see `docs/Kermi.Modbus.TCP_RTU_Quick.Guide_DE.pdf`.

## Features

- **Async/await support** - Modern async Python using `asyncio`
- **Two transports** - HTTP API (recommended) or Modbus TCP/RTU
- **Four device types** - IFM, Heat Pump, Storage System, and Universal Module
- **Fully typed** - Complete type hints for better IDE support
- **Type-safe enums** - Status and mode values as Python enums
- **Auto-conversion** - Automatic data type conversions
- **Validation** - Input validation with range checks
- **Device discovery** - Automatic detection of connected devices (HTTP)

## Installation

```bash
pip install kermi-xcenter
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### HTTP API (Recommended)

```python
import asyncio
from kermi_xcenter import KermiHttpClient

async def main():
    # Connect to x-center (password optional on some devices)
    client = KermiHttpClient(host="192.168.1.100", password="1234")

    async with client:
        # Devices are auto-discovered
        print(f"Found {len(client.devices)} devices")
        for device in client.devices:
            print(f"  - {device.display_name} (Unit {device.unit_id})")

        # Get all values efficiently (2 API calls)
        values = await client.get_all_values(unit_id=40)  # Heat Pump
        print(f"Outdoor: {values.get('outdoor_temperature')}°C")
        print(f"COP: {values.get('cop_total')}")
        print(f"Power: {values.get('power_total')} kW")

        # Get device info
        info = await client.get_device_info(unit_id=40)
        print(f"Model: {info.model}")
        print(f"Serial: {info.serial_number}")
        print(f"Firmware: {info.software_version}")

        # Read IFM (x-center gateway) data
        ifm_values = await client.get_all_values(unit_id=0)
        print(f"SmartGrid State: {ifm_values.get('ifm_smartgrid_state')}")
        print(f"S0 Power: {ifm_values.get('ifm_s0_power')} W")

        # Check alarms
        alarms = await client.get_current_alarms()
        if alarms:
            for alarm in alarms:
                print(f"Alarm: {alarm.message}")

asyncio.run(main())
```

### Modbus (Alternative)

```python
import asyncio
from kermi_xcenter import KermiModbusClient, HeatPump

async def main():
    client = KermiModbusClient(host="192.168.1.100", port=502)
    heat_pump = HeatPump(client)

    async with client:
        outdoor_temp = await heat_pump.get_outdoor_temperature()
        cop = await heat_pump.get_cop_total()
        status = await heat_pump.get_heat_pump_status()

        print(f"Outdoor: {outdoor_temp}°C")
        print(f"COP: {cop}")
        print(f"Status: {status.name}")

asyncio.run(main())
```

## Supported Devices

### IFM - x-center Interface Module (Unit 0, HTTP only)

The x-center gateway device itself:
- System info (serial, firmware, OS version)
- Network status (LAN states, IP, remote connection)
- SmartGrid/EVU signals (EVU, SGReady2, SmartGrid state)
- Digital I/O (LED1, LED2, Output1, Output2)
- S0 energy meter (power, pulse counter)

```python
# HTTP only
values = await client.get_all_values(unit_id=0)
smartgrid = values.get('ifm_smartgrid_state')  # 0-4
evu_active = values.get('ifm_evu_signal')       # True/False
s0_power = values.get('ifm_s0_power')           # Watts
```

### Heat Pump (Unit 40)

Main heat pump control:
- Energy source temperatures
- Heat pump circuit (supply, return, flow rate)
- COP values (total, heating, hot water, cooling)
- Power measurements (thermal and electrical)
- Operating hours (fan, compressor, pumps)
- Status and alarms
- PV modulation controls

```python
# HTTP
values = await client.get_all_values(unit_id=40)
cop = values.get('cop_total')

# Modbus
from kermi_xcenter import HeatPump
heat_pump = HeatPump(client, unit_id=40)
cop = await heat_pump.get_cop_total()
```

### Storage System (Units 50/51)

Heating storage (50) and hot water storage (51):
- Storage temperatures (heating, cooling, hot water)
- Heating circuit control
- Operating modes and energy settings
- External heat generator control

```python
# HTTP
heating_values = await client.get_all_values(unit_id=50)
hot_water_values = await client.get_all_values(unit_id=51)

# Modbus
from kermi_xcenter import StorageSystem
heating_storage = StorageSystem(client, unit_id=50)
hot_water_storage = StorageSystem(client, unit_id=51)
```

### Universal Module (Unit 30, Modbus only)

Additional heating circuits:
- Heating circuit control and status
- Operating modes and energy settings

```python
from kermi_xcenter import UniversalModule
universal = UniversalModule(client, unit_id=30)
```

## Writing Values

### HTTP

```python
# Set hot water boost
await client.set_value("hot_water_boost_active", True, unit_id=51)
await client.set_value("hot_water_boost_setpoint", 55.0, unit_id=51)

# Control IFM outputs
await client.set_value("ifm_led1", True, unit_id=0)
await client.set_value("ifm_output1", False, unit_id=0)
```

### Modbus

```python
await heat_pump.set_pv_modulation_power(2000)  # 2000W
await storage.set_hot_water_setpoint_constant(50.0)
await storage.set_heating_circuit_energy_mode(EnergyMode.ECO)
```

## Connection Types

### HTTP

```python
client = KermiHttpClient(
    host="192.168.1.100",
    password="1234",      # Optional on some devices
    port=80,              # Default HTTP port
    timeout=10.0
)
```

### Modbus TCP

```python
client = KermiModbusClient(
    host="192.168.1.100",
    port=502,
    timeout=3.0,
    retries=3
)
```

### Modbus RTU

```python
client = KermiModbusClient(
    port="/dev/ttyUSB0",
    baudrate=9600,
    use_rtu=True,
    timeout=3.0
)
```

## Examples

See the `examples/` directory:

- **`http_monitoring.py`** - HTTP client with device discovery and bulk reads
- **`basic_monitoring.py`** - Modbus: Read temperatures, COP, power, and status
- **`pv_modulation.py`** - Modbus: Control PV modulation for solar integration
- **`storage_control.py`** - Modbus: Control heating and hot water storage
- **`continuous_monitoring.py`** - Modbus: Continuous monitoring with periodic updates

Run an example:

```bash
python examples/http_monitoring.py --host 192.168.1.100 --password 1234
python examples/basic_monitoring.py
```

## Data Types and Enums

```python
from kermi_xcenter import (
    HeatPumpStatus,           # STANDBY, ALARM, HOT_WATER, COOLING, HEATING, etc.
    HeatingCircuitStatus,     # OFF, HEATING, COOLING, DEW_POINT, etc.
    OperatingMode,            # OFF, HEATING, COOLING
    OperatingType,            # AUTO, HEATING
    EnergyMode,               # OFF, ECO, NORMAL, COMFORT, CUSTOM
    SeasonSelection,          # AUTO, HEATING, COOLING, OFF
    ExternalHeatGeneratorMode,  # AUTO, HEAT_PUMP_ONLY, BOTH, SECONDARY_ONLY
)
```

## Error Handling

```python
from kermi_xcenter import (
    KermiModbusError,          # Base exception
    ConnectionError,           # Connection failed
    RegisterReadError,         # Read operation failed
    RegisterWriteError,        # Write operation failed
    ValidationError,           # Value out of range
    HttpError,                 # HTTP API error
    AuthenticationError,       # HTTP authentication failed
    DatapointNotWritableError, # Attempted write to read-only datapoint
)

try:
    values = await client.get_all_values(unit_id=40)
except HttpError as e:
    print(f"HTTP API error: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

## Architecture

```
kermi_xcenter/
├── client.py              # Async Modbus client (TCP/RTU)
├── http/
│   ├── client.py          # Async HTTP client
│   ├── session.py         # HTTP session management
│   ├── mapping.py         # WellKnownName to attribute mapping
│   └── models.py          # HTTP data models
├── registers.py           # Modbus register definitions
├── types.py               # Enums and type aliases
├── exceptions.py          # Custom exceptions
└── models/
    ├── base.py            # Base device class
    ├── heat_pump.py       # Heat pump (unit 40)
    ├── storage_system.py  # Storage system (units 50/51)
    └── universal_module.py # Universal module (unit 30)
```

## Documentation

- [HTTP API Specification](docs/http_specification.md) - HTTP endpoints and datapoints
- [OpenAPI Specification](docs/openapi.yaml) - Machine-readable API spec
- [Modbus Specification](docs/modbus_specification.md) - Complete register maps
- [Project Plan](docs/project_plan.md) - Architecture and design decisions

## Development

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Code Quality

```bash
black src/ tests/ examples/
ruff check src/ tests/ examples/
mypy src/
pytest
```

## Requirements

- Python 3.12+
- pymodbus >= 3.6.0
- aiohttp >= 3.9.0

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code passes linting and type checking
5. Submit a pull request

## Credits

This library is not affiliated with or endorsed by Kermi GmbH.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation in `docs/`
- Review examples in `examples/`

## Changelog

### 0.3.0 (2026-01-06)

- Added HTTP API client (`KermiHttpClient`) as recommended transport
- Added IFM device support (SmartGrid, I/O, S0 meter)
- Added automatic device discovery
- Added efficient bulk reads (all datapoints in 2 API calls)
- Added alarm management (current and history)
- Added 40+ IFM datapoint mappings
- Added 180+ Heat Pump and Storage datapoint mappings
- Added HTTP API documentation and OpenAPI spec
- Tested with x-center IFM firmware 1.6.3.42

### 0.2.2 (2025-12-01)

- Fixed power and COP scaling (10x correction)

### 0.2.1 (2025-11-27)

- Added Codecov integration
- Fixed cleanup errors from malformed frames

### 0.2.0 (2025-11-27)

- Return None for unavailable registers (Pythonic API)
- Added resilient error handling for device firmware variations

### 0.1.0 (2025-11-27)

- Initial release
- Async/await support for all operations
- Support for three device types (Heat Pump, Storage System, Universal Module)
- Complete register definitions with English names
- Type-safe enums for all status and mode values
- Automatic data conversions
- TCP and RTU connection support

---

## Disclaimer

**This software is provided "as-is" without any warranty of any kind, express or implied.**

- The **HTTP API implementation** interfaces with an unofficial, undocumented API of the Kermi x-center. This API may change without notice in firmware updates, potentially breaking functionality.

- The **Modbus implementation** is based on Kermi's official Modbus documentation.

- This library is not affiliated with, endorsed by, or supported by Kermi GmbH.

- Use at your own risk. The authors are not responsible for any damage to your equipment, loss of warranty, or other issues that may arise from using this software.

- Always ensure you have appropriate backups and understand the implications before writing values to your heat pump system.
