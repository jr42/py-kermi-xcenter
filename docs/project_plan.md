# Kermi Modbus Python Module - Project Plan

## Overview

Create a clean, best-practice Python module for interfacing with Kermi heat pumps via Modbus protocol. The module will expose multiple devices (heat pump, floor heating, warm water heating) through a well-structured API.

## Project Structure

```
py-kermi-xcenter/
├── src/
│   └── kermi_modbus/
│       ├── __init__.py
│       ├── client.py              # Main Modbus client wrapper
│       ├── exceptions.py          # Custom exceptions
│       ├── types.py               # Type definitions and enums
│       ├── registers.py           # Register definitions and mappings
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py            # Base device class
│       │   ├── waermepumpe.py     # Heat pump module (unit 40)
│       │   ├── speichersystem.py  # Storage system module (units 50/51)
│       │   └── universalmodul.py  # Universal module (unit 30)
│       └── utils/
│           ├── __init__.py
│           └── conversions.py     # Data type conversions (temp, power, etc.)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration and fixtures
│   ├── test_client.py
│   ├── test_waermepumpe.py
│   ├── test_speichersystem.py
│   ├── test_universalmodul.py
│   └── test_conversions.py
├── docs/
│   ├── modbus_specification.md    # ✓ Already created
│   ├── project_plan.md            # This file
│   ├── api_reference.md           # To be created
│   └── examples.md                # Usage examples
├── examples/
│   ├── read_temperatures.py
│   ├── read_cop_values.py
│   ├── write_pv_modulation.py
│   └── monitor_heat_pump.py
├── pyproject.toml                 # Modern Python project configuration
├── README.md
├── LICENSE
└── .gitignore
```

## Technology Stack

### Core Dependencies
- **pymodbus** (>=3.0.0): Robust Modbus communication library
  - Supports both RTU and TCP
  - Well-maintained and actively developed
  - Async support for future expansion

### Development Dependencies
- **pytest** (>=7.0): Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support
- **ruff**: Fast Python linter (replaces flake8, isort, etc.)
- **black**: Code formatter
- **mypy**: Static type checker
- **pre-commit**: Git hooks for code quality

## Module Design

### 1. Client Layer (`client.py`)

**Purpose**: Abstraction over pymodbus for Kermi-specific operations

**Key Features**:
- Connect to Modbus RTU or TCP
- Read/write operations with automatic retry logic
- Handle data type conversions (INT16, scaling factors)
- Connection management (context manager support)
- Error handling and logging

**API Example**:
```python
class KermiModbusClient:
    def __init__(self, host: str, port: int = 502, unit_id: int = 40)
    def connect(self) -> None
    def disconnect(self) -> None
    def read_register(self, address: int) -> int
    def read_registers(self, address: int, count: int) -> list[int]
    def write_register(self, address: int, value: int) -> None
    def write_registers(self, address: int, values: list[int]) -> None
```

### 2. Register Definitions (`registers.py`)

**Purpose**: Central registry of all Modbus registers

**Approach**: Dataclass-based register definitions
```python
@dataclass
class RegisterDef:
    address: int
    name: str
    description: str
    unit: str
    attribute: Literal["R", "R/W"]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[float] = None
    enum_mapping: Optional[dict[int, str]] = None
    scaling_factor: float = 1.0
    data_type: Literal["int16", "uint16"] = "int16"
```

**Register Maps**:
- `WAERMEPUMPE_REGISTERS`: Unit 40 register definitions
- `SPEICHERSYSTEM_REGISTERS`: Units 50/51 register definitions
- `UNIVERSALMODUL_REGISTERS`: Unit 30 register definitions

### 3. Type Definitions (`types.py`)

**Purpose**: Enums and type aliases for strong typing

**Includes**:
- `HeatPumpStatus`: Enum for status values (Standby, Alarm, TWE, etc.)
- `HeatingCircuitStatus`: Enum for heating circuit states
- `Betriebsmodus`: Operating mode enum
- `Energiemodus`: Energy mode enum
- Type aliases for clarity

### 4. Device Models (`models/`)

**Base Class** (`base.py`):
```python
class KermiDevice:
    def __init__(self, client: KermiModbusClient, unit_id: int)
    def _read_register(self, register: RegisterDef) -> Union[float, int, str]
    def _write_register(self, register: RegisterDef, value: Union[float, int]) -> None
    def get_all_values(self) -> dict[str, Any]
```

**Heat Pump** (`waermepumpe.py`):
```python
class Waermepumpe(KermiDevice):
    def get_energiequelle_austritt(self) -> float
    def get_aussentemperatur(self) -> float
    def get_cop_aktuell(self) -> float
    def get_leistung_aktuell(self) -> float
    def get_status(self) -> HeatPumpStatus
    def set_pv_modulation_leistung(self, watts: int) -> None
    # ... all other register accessors
```

**Storage System** (`speichersystem.py`):
```python
class Speichersystem(KermiDevice):
    def get_heizen_ist(self) -> float
    def get_twe_ist(self) -> float
    def set_twe_soll_konstant(self, temp: float) -> None
    def get_heizkreis_status(self) -> HeatingCircuitStatus
    # ... all other register accessors
```

**Universal Module** (`universalmodul.py`):
```python
class Universalmodul(KermiDevice):
    def get_heizkreis_ist(self) -> float
    def get_betriebsmodus(self) -> Betriebsmodus
    # ... all other register accessors
```

### 5. Utilities (`utils/conversions.py`)

**Data Conversion Functions**:
```python
def raw_to_temperature(value: int) -> float:
    """Convert INT16 raw value to temperature in °C (0.1°C units)"""
    return value / 10.0

def temperature_to_raw(temp: float) -> int:
    """Convert temperature in °C to INT16 raw value"""
    return int(temp * 10)

def raw_to_power(value: int) -> float:
    """Convert UINT16 raw value to power in kW (0.01 kW units)"""
    return value / 100.0

def raw_to_cop(value: int) -> float:
    """Convert UINT16 raw value to COP (0.01 units)"""
    return value / 100.0
```

## Configuration (`pyproject.toml`)

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kermi-modbus"
version = "0.1.0"
description = "Python interface for Kermi heat pumps via Modbus"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.9"
license = {text = "Apache-2.0"}
dependencies = [
    "pymodbus>=3.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
    "ruff>=0.1.0",
    "black>=23.0",
    "mypy>=1.0",
    "pre-commit>=3.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.black]
line-length = 100
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

## Testing Strategy

### Unit Tests
- Mock pymodbus client for isolated testing
- Test each device class independently
- Validate data conversions
- Test error handling

### Integration Tests (Optional)
- Test against a simulated Modbus server
- Use `pymodbus.server` for simulation

### Test Coverage Goals
- Minimum 80% code coverage
- 100% coverage for critical paths (data conversions, register reads/writes)

## Error Handling

### Custom Exceptions
```python
class KermiModbusError(Exception):
    """Base exception for kermi_modbus"""

class ConnectionError(KermiModbusError):
    """Connection to Modbus device failed"""

class RegisterReadError(KermiModbusError):
    """Failed to read register"""

class RegisterWriteError(KermiModbusError):
    """Failed to write register"""

class ValidationError(KermiModbusError):
    """Value validation failed (out of range, etc.)"""
```

## Code Quality Standards

### Formatting
- **black**: Automatic code formatting (line length: 100)
- **ruff**: Linting, import sorting, style checks

### Type Hints
- Full type annotations for all public APIs
- Use `mypy --strict` mode
- Document complex types with TypedDict or dataclasses

### Documentation
- Docstrings for all public classes and methods (Google style)
- Type hints in all function signatures
- Inline comments for complex logic

### Best Practices
- Use context managers for connection management
- Implement proper logging (using Python's `logging` module)
- Follow PEP 8 style guide
- Immutable defaults (no mutable default arguments)
- Defensive programming (validate inputs, handle edge cases)

## Example Usage

```python
from kermi_modbus import KermiModbusClient, Waermepumpe, Speichersystem

# Connect to heat pump via Modbus TCP
client = KermiModbusClient(host="192.168.1.100", port=502)

# Create device instances
heat_pump = Waermepumpe(client, unit_id=40)
storage_heating = Speichersystem(client, unit_id=50)
storage_twe = Speichersystem(client, unit_id=51)

# Read values
with client:
    # Heat pump readings
    temp_outside = heat_pump.get_aussentemperatur()
    cop = heat_pump.get_cop_aktuell()
    power = heat_pump.get_leistung_aktuell()
    status = heat_pump.get_status()

    print(f"Outside: {temp_outside}°C")
    print(f"COP: {cop}")
    print(f"Power: {power} kW")
    print(f"Status: {status.name}")

    # Storage readings
    temp_heating = storage_heating.get_heizen_ist()
    temp_twe = storage_twe.get_twe_ist()

    # Write values (PV modulation)
    heat_pump.set_pv_modulation_leistung(2000)  # 2000W
    storage_twe.set_twe_soll_konstant(50.0)  # 50°C
```

## Development Workflow

1. **Initial Setup**
   - Create project structure
   - Set up `pyproject.toml`
   - Initialize git repository
   - Create virtual environment

2. **Core Implementation**
   - Implement base client
   - Define register mappings
   - Implement data conversions
   - Create device classes

3. **Testing**
   - Write unit tests
   - Set up pytest configuration
   - Add CI/CD (GitHub Actions)

4. **Documentation**
   - Complete API reference
   - Write usage examples
   - Update README

5. **Refinement**
   - Code review
   - Performance optimization
   - Error handling improvements

## Future Enhancements (Post-MVP)

1. **Async Support**: Add async methods using `asyncio` and async pymodbus
2. **Auto-discovery**: Detect available modules on the bus
3. **Caching**: Cache register values with TTL to reduce Modbus traffic
4. **Home Assistant Integration**: Create a Home Assistant custom component
5. **CLI Tool**: Command-line interface for quick queries
6. **MQTT Bridge**: Publish values to MQTT for integration with other systems
7. **Historical Data**: Log and store historical values
8. **Alarms/Notifications**: Monitor for alarm conditions

## Success Criteria

- Clean, well-documented codebase
- Full type hints with mypy validation
- >80% test coverage
- All device modules working correctly
- Example scripts demonstrating usage
- Ready for PyPI publication
