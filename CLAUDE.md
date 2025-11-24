# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an async Python library for interfacing with Kermi heat pumps via Modbus protocol (TCP and RTU). The library provides type-safe, async/await access to three device types: Heat Pump (unit 40), Storage System (units 50/51), and Universal Module (unit 30).

**Key constraint**: Python 3.12+ minimum (uses modern type hints and async features).

## Development Commands

### Environment Setup
```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if needed)
pre-commit install
```

### Code Quality (run these before committing)
```bash
# Format code
black src/ tests/ examples/

# Lint (use new config format)
ruff check src/ tests/ examples/

# Auto-fix linting issues
ruff check --fix src/ tests/ examples/

# Type check
mypy src/
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run specific test class
pytest tests/test_client.py::TestClientConnection

# Run specific test
pytest tests/test_client.py::TestClientConnection::test_tcp_client_creation

# Run with coverage
pytest --cov=kermi_xcenter --cov-report=html

# Run with verbose output
pytest -v
```

## Pre-Commit Checklist

**ALWAYS run these checks before committing:**

```bash
# 1. Format code with black
black src/ tests/ examples/

# 2. Run ruff linter
ruff check src/ tests/ examples/

# 3. Run type checker
mypy src/

# 4. Run test suite
pytest

# Quick one-liner to run all checks:
black src/ tests/ examples/ && ruff check src/ tests/ examples/ && mypy src/ && pytest
```

All checks must pass before committing. The CI pipeline will fail if any of these checks fail.

## Commit Message Convention

This project uses **semantic commit messages** following the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format
```
type(scope): subject

body (optional)

footer (optional)
```

### Types
- **feat**: New feature (e.g., `feat(heat-pump): add PV modulation control`)
- **fix**: Bug fix (e.g., `fix(client): handle connection timeout in retry logic`)
- **docs**: Documentation changes (e.g., `docs: update README with RTU example`)
- **style**: Code style/formatting (e.g., `style: apply black formatting`)
- **refactor**: Code refactoring (e.g., `refactor(models): extract common validation logic`)
- **test**: Adding or updating tests (e.g., `test(storage): add hot water setpoint tests`)
- **chore**: Maintenance tasks (e.g., `chore: update pymodbus to 3.7.0`)
- **perf**: Performance improvements (e.g., `perf(client): add register caching`)
- **ci**: CI/CD changes (e.g., `ci: add Python 3.13 to test matrix`)

### Scopes (optional but recommended)
- `client` - KermiModbusClient
- `heat-pump` - HeatPump model
- `storage` - StorageSystem model
- `universal` - UniversalModule model
- `types` - Type definitions and enums
- `registers` - Register definitions
- `conversions` - Data conversion utilities
- `tests` - Test suite
- `docs` - Documentation

### Examples
```
feat(heat-pump): add COP monitoring methods

Add methods to read COP values for heating, cooling, and hot water.
Includes automatic conversion from 0.01 units to float.

fix(client): use device_id parameter instead of slave

Update for pymodbus 3.6.0 API compatibility. The slave parameter
was deprecated in favor of device_id.

Fixes #42

docs(readme): add installation instructions

test(storage): add validation tests for temperature ranges

chore(deps): update pymodbus to 3.7.0
```

### Breaking Changes
For breaking changes, add `BREAKING CHANGE:` in the footer:
```
feat(client)!: require Python 3.12+

BREAKING CHANGE: Dropped support for Python 3.11 and earlier
to use modern async features and type hints.
```

## Architecture Overview

### Layered Design

1. **Client Layer** (`src/kermi_xcenter/client.py`)
   - `KermiModbusClient`: Async wrapper around pymodbus
   - Handles TCP and RTU connections
   - Provides retry logic with exponential backoff (default: 3 retries)
   - **Critical**: Uses `device_id` parameter (not `slave`) for pymodbus >=3.6.0
   - Context manager support for automatic connect/disconnect

2. **Register Layer** (`src/kermi_xcenter/registers.py`)
   - Centralized register definitions using `RegisterDef` dataclass
   - Three register maps: `HEAT_PUMP_REGISTERS`, `STORAGE_SYSTEM_REGISTERS`, `UNIVERSAL_MODULE_REGISTERS`
   - Each register defines: address, name, unit, attribute (R/R/W), data type, min/max, converters
   - Register names use English (German names preserved in docstrings)

3. **Model Layer** (`src/kermi_xcenter/models/`)
   - `base.py`: `KermiDevice` base class with common register read/write logic
   - `heat_pump.py`: `HeatPump` class (unit 40) - main heat pump control
   - `storage_system.py`: `StorageSystem` class (units 50/51) - heating and hot water storage
   - `universal_module.py`: `UniversalModule` class (unit 30) - additional heating circuits
   - All methods are async and follow pattern: `get_*()` for reads, `set_*()` for writes

4. **Type Layer** (`src/kermi_xcenter/types.py`)
   - Type-safe enums for all status and mode values
   - `HeatPumpStatus`, `HeatingCircuitStatus`, `OperatingMode`, `EnergyMode`, etc.
   - All enums use `IntEnum` for Modbus compatibility

5. **Utility Layer** (`src/kermi_xcenter/utils/conversions.py`)
   - Data conversion functions between raw Modbus values and engineering units
   - Temperatures: INT16 in 0.1°C units ↔ float in °C
   - Power: UINT16 in 0.01 kW units ↔ float in kW
   - COP: UINT16 in 0.01 units ↔ float
   - Flow rate: UINT16 in 0.1 l/min units ↔ float in l/min

### Data Flow Pattern

```
User Code → Device Model → Base Device → Client → pymodbus → Modbus Device
           ← (with conversion) ← (raw value) ← ← ←
```

## Important Implementation Details

### Register Access Pattern

The `KermiDevice` base class provides two core methods:
- `_read_register(register: RegisterDef)`: Reads raw value, applies converter if defined, returns typed value
- `_write_register(register: RegisterDef, value)`: Validates value, applies inverse_converter if defined, writes raw value

Device classes expose these as public getter/setter methods:
```python
async def get_outdoor_temperature(self) -> float:
    """Get outdoor temperature in °C."""
    return await self._read_register(self.registers["outdoor_temperature"])

async def set_pv_modulation_power(self, watts: int) -> None:
    """Set PV modulation power in Watts."""
    await self._write_register(self.registers["pv_modulation_power"], watts)
```

### Type Safety with Enums

When reading enum registers, cast the result to the appropriate enum:
```python
async def get_heat_pump_status(self) -> HeatPumpStatus:
    value = await self._read_register(self.registers["heat_pump_status"])
    return HeatPumpStatus(int(value))  # Explicit int() cast for type safety
```

### Validation

Write operations validate against register min/max values before writing:
- Raises `ValidationError` if value out of range
- Raises `ReadOnlyRegisterError` if attempting to write to R-only register

### Error Handling

Custom exception hierarchy:
- `KermiModbusError` (base)
  - `ConnectionError` - connection failures
  - `RegisterReadError` - read failures (includes address in error)
  - `RegisterWriteError` - write failures (includes address and value)
  - `ValidationError` - value validation failures
  - `ReadOnlyRegisterError` - write to read-only register

Retry logic catches ALL exceptions (not just ModbusException) to handle network errors properly.

## Testing Strategy

### Mock-Based Testing
- Tests use `AsyncMock` from `unittest.mock` for pymodbus client
- `conftest.py` provides fixtures: `mock_tcp_client`, `mock_modbus_response`, `kermi_client`
- Test pattern: mock response → call method → assert result and assert_called_with

### Test Organization
```
tests/
├── test_client.py           # Client connection, read/write, retry logic
├── test_heat_pump.py        # Heat pump device methods
├── test_storage_system.py   # Storage system device methods
├── test_universal_module.py # Universal module device methods
├── test_exceptions.py       # Exception hierarchy and validation
├── test_conversions.py      # Data conversion utilities
└── test_init.py            # Package imports
```

### Known Test Limitation
One test (`test_rtu_client_creation`) fails without `pyserial` installed. This is expected behavior as RTU is an optional feature requiring serial port hardware.

## Code Quality Configuration

### Ruff (new format in pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]  # Note: NEW format, not top-level
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports

[tool.ruff.lint.isort]
known-first-party = ["kermi_xcenter"]
```

### MyPy
Strict mode enabled. Common fixes needed:
- Explicit `int()` casts when passing to enum constructors
- Explicit `bool()` or `int()` casts for return types when base method returns `float | int | bool`

### Black
Line length: 100 characters

## Common Gotchas

1. **pymodbus API change**: The parameter changed from `slave=` to `device_id=` in pymodbus 3.6.0. Always use `device_id` in read/write calls.

2. **Async everywhere**: All device methods are async. Don't forget `await`.

3. **Unit IDs matter**:
   - Heat Pump: 40
   - Heating Storage: 50
   - Hot Water Storage: 51
   - Universal Module: 30

4. **Type casts for type safety**: When reading enums or when mypy complains about return types, add explicit casts:
   ```python
   return HeatPumpStatus(int(value))  # Not just HeatPumpStatus(value)
   return bool(await self._read_register(...))  # For bool returns
   return int(await self._read_register(...))   # For int returns
   ```

5. **German vs English naming**: Code uses English names, but docstrings include German names from Kermi spec for reference.

## Reference Documentation

- `docs/modbus_specification.md`: Complete Modbus register maps with German names
- `docs/project_plan.md`: Original architecture design decisions
- `examples/`: Working code examples for common use cases
