# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.1.0
[0.0.1]: https://github.com/jr42/py-kermi-xcenter/releases/tag/v0.0.1
