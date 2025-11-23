# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of kermi-modbus package
- Async/await support for all I/O operations
- Support for three device types:
  - HeatPump (Unit ID 40)
  - StorageSystem (Units 50/51)
  - UniversalModule (Unit ID 30)
- Complete register definitions with English names
- Type-safe enums for all status and mode values
- Automatic data conversions (temperatures, power, COP, flow rate)
- Input validation with range checks
- TCP and RTU Modbus connection support
- Retry logic with exponential backoff
- Comprehensive test suite with 80+ test cases
- Four working examples demonstrating usage
- Complete documentation (README, Modbus spec, project plan)
- GitHub Actions workflows for CI/CD
- Security scanning with CodeQL
- Dependency management with Dependabot

### Device Features

#### HeatPump (Unit 40)
- Energy source temperature monitoring
- Heat pump circuit measurements (supply, return, flow rate)
- COP values (total, heating, hot water, cooling)
- Power measurements (thermal and electrical)
- Operating hours tracking
- Status and alarm monitoring
- PV modulation control

#### StorageSystem (Units 50/51)
- Heating and hot water storage temperatures
- Heating circuit control with status enums
- Operating modes and energy settings
- Season selection and automatic switching
- External heat generator control
- Temperature sensor readings (T1-T4, outdoor)
- Operating hours tracking

#### UniversalModule (Unit 30)
- Additional heating circuit support
- Operating mode and energy settings
- Heating curve adjustments
- Temperature sensor readings
- Season threshold configuration

### Technical Features
- Python 3.12+ with modern syntax
- Full type hints with mypy strict mode
- Async/await for all I/O operations
- Explicit getter/setter methods
- Dataclass-based register definitions
- Mock-based unit tests (no hardware required)
- Comprehensive error handling
- Connection retry logic

## [0.1.0] - TBD

### Added
- Initial release

[Unreleased]: https://github.com/jr42/py-kermi-xcenter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.1.0
