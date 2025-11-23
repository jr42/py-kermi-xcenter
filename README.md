# Kermi Modbus

Async Python interface for Kermi heat pumps via Modbus (TCP/RTU).

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Features

- ✨ **Async/await support** - Modern async Python using `asyncio`
- 🔌 **TCP and RTU** - Supports both Modbus TCP and RTU connections
- 📊 **Three device types** - Heat Pump, Storage System, and Universal Module
- 🎯 **Fully typed** - Complete type hints for better IDE support
- 🛡️ **Type-safe enums** - Status and mode values as Python enums
- 🔄 **Auto-conversion** - Automatic data type conversions (temperatures, power, COP, etc.)
- ✅ **Validation** - Input validation with range checks
- 🔁 **Retry logic** - Automatic retries with exponential backoff
- 📝 **Well documented** - Comprehensive docstrings and examples

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from kermi_modbus import KermiModbusClient, HeatPump

async def main():
    # Create client
    client = KermiModbusClient(host="192.168.1.100", port=502)

    # Create heat pump device (unit ID 40)
    heat_pump = HeatPump(client)

    # Connect and read values
    async with client:
        # Read temperatures
        outdoor_temp = await heat_pump.get_outdoor_temperature()
        supply_temp = await heat_pump.get_supply_temp_heat_pump()

        # Read COP (Coefficient of Performance)
        cop = await heat_pump.get_cop_total()

        # Read power
        power_thermal = await heat_pump.get_power_total()
        power_electrical = await heat_pump.get_power_electrical_total()

        # Get status
        status = await heat_pump.get_heat_pump_status()

        print(f"Outdoor: {outdoor_temp}°C")
        print(f"Supply:  {supply_temp}°C")
        print(f"COP:     {cop}")
        print(f"Power:   {power_thermal} kW (thermal), {power_electrical} kW (electrical)")
        print(f"Status:  {status.name}")

asyncio.run(main())
```

## Supported Devices

### Heat Pump (Unit ID 40)

Main heat pump control with access to:
- Energy source temperatures
- Heat pump circuit (supply, return, flow rate)
- COP values (total, heating, hot water, cooling)
- Power measurements (thermal and electrical)
- Operating hours (fan, compressor, pumps)
- Status and alarms
- PV modulation controls

```python
from kermi_modbus import HeatPump

heat_pump = HeatPump(client, unit_id=40)
cop = await heat_pump.get_cop_total()
await heat_pump.set_pv_modulation_power(2000)  # 2000W
```

### Storage System (Units 50/51)

Heating storage (50) and hot water storage (51):
- Storage temperatures (heating, cooling, hot water)
- Heating circuit control
- Operating modes and energy settings
- Season selection
- External heat generator control
- Temperature sensors
- Operating hours

```python
from kermi_modbus import StorageSystem, EnergyMode

heating_storage = StorageSystem(client, unit_id=50)
hot_water_storage = StorageSystem(client, unit_id=51)

temp = await heating_storage.get_heating_actual()
await hot_water_storage.set_hot_water_setpoint_constant(50.0)
await heating_storage.set_heating_circuit_energy_mode(EnergyMode.ECO)
```

### Universal Module (Unit ID 30)

Additional heating circuits with:
- Heating circuit control and status
- Operating modes and energy settings
- Season selection
- Temperature sensors
- Operating hours

```python
from kermi_modbus import UniversalModule, EnergyMode

universal = UniversalModule(client, unit_id=30)
await universal.set_energy_mode(EnergyMode.COMFORT)
```

## Connection Types

### TCP Connection

```python
client = KermiModbusClient(
    host="192.168.1.100",
    port=502,
    timeout=3.0,
    retries=3
)
```

### RTU Connection

```python
client = KermiModbusClient(
    port="/dev/ttyUSB0",
    baudrate=9600,
    use_rtu=True,
    timeout=3.0
)
```

## Examples

See the `examples/` directory for complete examples:

- **`basic_monitoring.py`** - Read temperatures, COP, power, and status
- **`pv_modulation.py`** - Control PV modulation for solar integration
- **`storage_control.py`** - Control heating and hot water storage
- **`continuous_monitoring.py`** - Continuous monitoring with periodic updates

Run an example:

```bash
python examples/basic_monitoring.py
```

## Data Types and Enums

The library provides type-safe enums for all status and mode values:

```python
from kermi_modbus import (
    HeatPumpStatus,           # STANDBY, ALARM, HOT_WATER, COOLING, HEATING, etc.
    HeatingCircuitStatus,     # OFF, HEATING, COOLING, DEW_POINT, etc.
    OperatingMode,            # OFF, HEATING, COOLING
    OperatingType,            # AUTO, HEATING
    EnergyMode,               # OFF, ECO, NORMAL, COMFORT, CUSTOM
    SeasonSelection,          # AUTO, HEATING, COOLING, OFF
    ExternalHeatGeneratorMode,  # AUTO, HEAT_PUMP_ONLY, BOTH, SECONDARY_ONLY
)
```

## Automatic Data Conversion

All register values are automatically converted to engineering units:

- **Temperatures**: Stored as INT16 in 0.1°C units, returned as `float` in °C
- **Power**: Stored as UINT16 in 0.01 kW units, returned as `float` in kW
- **COP**: Stored as UINT16 in 0.01 units, returned as `float`
- **Flow rate**: Stored as UINT16 in 0.1 l/min units, returned as `float` in l/min
- **Booleans**: Stored as UINT16 (0/1), returned as `bool`
- **Enums**: Stored as UINT16, returned as typed enum instances

## Error Handling

The library provides custom exceptions for different error scenarios:

```python
from kermi_modbus import (
    KermiModbusError,          # Base exception
    ConnectionError,           # Connection failed
    RegisterReadError,         # Read operation failed
    RegisterWriteError,        # Write operation failed
    ValidationError,           # Value out of range
    ReadOnlyRegisterError,     # Attempted write to read-only register
)

try:
    temp = await heat_pump.get_outdoor_temperature()
except RegisterReadError as e:
    print(f"Failed to read register {e.address}: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

## Register Documentation

All register names use English for code clarity, with German equivalents preserved in docstrings:

```python
# English method name
outdoor_temp = await heat_pump.get_outdoor_temperature()

# Docstring includes German reference:
# """Get outdoor temperature in °C.
#
# Kermi code: BOT, Register: 3
# German: Außentemperaturfühler
# """
```

Complete register specification: [`docs/modbus_specification.md`](docs/modbus_specification.md)

## Architecture

```
kermi_modbus/
├── client.py              # Async Modbus client (TCP/RTU)
├── registers.py           # Register definitions for all modules
├── types.py               # Enums and type aliases
├── exceptions.py          # Custom exceptions
├── utils/
│   └── conversions.py     # Data type conversion functions
└── models/
    ├── base.py            # Base device class
    ├── heat_pump.py       # Heat pump (unit 40)
    ├── storage_system.py  # Storage system (units 50/51)
    └── universal_module.py # Universal module (unit 30)
```

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ tests/ examples/

# Lint
ruff check src/ tests/ examples/

# Type check
mypy src/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=kermi_modbus --cov-report=html
```

## Modbus Function Codes

The library supports the following Modbus function codes:
- **0x03** - Read Holding Registers
- **0x06** - Write Single Register
- **0x10** - Write Multiple Registers

## Requirements

- Python 3.12+
- pymodbus >= 3.6.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code passes linting and type checking
5. Submit a pull request

## Credits

This library is not affiliated with or endorsed by Kermi GmbH.

## Documentation

- [Modbus Specification](docs/modbus_specification.md) - Complete register maps
- [Project Plan](docs/project_plan.md) - Architecture and design decisions

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation in `docs/`
- Review examples in `examples/`

## Changelog

### 0.1.0 (2025-01-XX)

- Initial release
- Async/await support for all operations
- Support for three device types (Heat Pump, Storage System, Universal Module)
- Complete register definitions with English names
- Type-safe enums for all status and mode values
- Automatic data conversions
- TCP and RTU connection support
- Comprehensive examples
