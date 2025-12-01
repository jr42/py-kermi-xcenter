# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-12-01

### Fixed
- **CRITICAL**: Power and COP conversion scaling corrected (values were 10x too low)
  - Power values now correctly use 0.1 kW units (was incorrectly 0.01 kW)
  - COP values now correctly use 0.1 units (was incorrectly 0.01 units)
  - Actual device behavior uses 0.1 scaling, matching temperature convention
  - Note: Official spec documents 0.01 units, but devices use 0.1 units

### Changed
- Updated README to refer to "Kermi x-center module" for clarity
- Added hardware compatibility section (x-buffer combi pro + x-change dynamic pro ac 6 AW E)
- Added Modbus activation requirement notice

### Documentation
- Conversion functions now document spec vs. reality discrepancy
- Added note about operating hours scaling uncertainty
- Updated all test expectations to match corrected conversion values

## [0.2.1] - 2025-11-27

### Fixed
- Suppress pymodbus/asyncio cleanup stack traces when malformed frames leave bytes in the buffer, keeping disconnects quiet after successful runs.

## [0.2.0] - 2025-11-27

### Added
- Pythonic `None` handling across all getter methods so unavailable registers return `Type | None` instead of raising `RegisterUnsupportedError`.
- Capability discovery utilities (`discover_capabilities()`, `save_capabilities()`, `load_capabilities()`, `merge_capabilities()`) for probing and persisting supported registers.
- Register validation fields (`min_valid_value` / `max_valid_value`) to automatically filter clearly invalid sensor readings.
- Demo script `demo_v0.2.0.py` showcasing the discovery workflow.

### Changed
- Automatic connection recovery moved into `KermiDevice._read_register()` so every getter benefits from the resilient retry logic.
- Device constructors accept cached capability maps to skip probing phases once a system is known.

## [0.1.0] - 2025-01-27

### Added
- `KermiModbusClient.reconnect()` method for connection recovery after protocol errors
- `RegisterUnsupportedError` exception for unsupported registers on specific device firmware
- `DataConversionError` exception for data conversion failures
- Automatic connection recovery in `get_all_readable_values()` after malformed Modbus frames
- Fail-fast logic for `ModbusIOException` to skip retries on permanent firmware bugs
- Enhanced exception chain checking to detect wrapped exceptions

### Changed
- **BREAKING**: Default timeout reduced from 3.0s to 1.0s for faster error detection
- `get_all_readable_values()` now resilient to device firmware variations
- Unsupported registers now return `None` instead of raising exceptions
- Exception handling now traverses full exception chain to detect protocol errors

### Performance
- **8x speedup** for batch operations with malformed registers (10:42 → 1:19)
- Reduced retry overhead through fail-fast logic on permanent errors
- Faster timeout for quicker failure detection

### Fixed
- Connection corruption from malformed Modbus frames no longer affects subsequent reads
- Batch operations now complete successfully despite firmware bugs in individual registers

## [0.0.1] - 2024-11-25

### Added
- Initial release of kermi-xcenter
- Async Python interface for Kermi heat pumps via Modbus (TCP/RTU)
- Support for HeatPump (Unit 40), StorageSystem (Units 50/51), and UniversalModule (Unit 30)
- Comprehensive register definitions, type-safe enums, and automatic data conversions
- Full test suite with 81% coverage

[0.2.2]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.2.2
[0.2.1]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.2.1
[0.2.0]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.2.0
[0.1.0]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.1.0
[0.0.1]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.0.1
