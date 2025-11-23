"""Tests for __init__.py."""

import pytest


class TestPackageImports:
    """Test that all public classes can be imported."""

    def test_import_client(self):
        """Test importing client."""
        from kermi_modbus import KermiModbusClient
        assert KermiModbusClient is not None

    def test_import_devices(self):
        """Test importing device classes."""
        from kermi_modbus import HeatPump, StorageSystem, UniversalModule, KermiDevice
        assert HeatPump is not None
        assert StorageSystem is not None
        assert UniversalModule is not None
        assert KermiDevice is not None

    def test_import_exceptions(self):
        """Test importing exceptions."""
        from kermi_modbus import (
            KermiModbusError,
            ConnectionError,
            RegisterReadError,
            RegisterWriteError,
            ValidationError,
            ReadOnlyRegisterError,
        )
        assert KermiModbusError is not None
        assert ConnectionError is not None

    def test_import_enums(self):
        """Test importing enum types."""
        from kermi_modbus import (
            HeatPumpStatus,
            HeatingCircuitStatus,
            OperatingMode,
            OperatingType,
            EnergyMode,
            SeasonSelection,
            ExternalHeatGeneratorMode,
            ExternalHeatGeneratorStatus,
            BooleanValue,
        )
        assert HeatPumpStatus is not None
        assert HeatingCircuitStatus is not None
        assert EnergyMode is not None

    def test_version_defined(self):
        """Test that version is defined."""
        from kermi_modbus import __version__
        assert __version__ == "0.1.0"

    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        from kermi_modbus import __all__

        expected = {
            "__version__",
            "KermiModbusClient",
            "KermiDevice",
            "HeatPump",
            "StorageSystem",
            "UniversalModule",
            "KermiModbusError",
            "ConnectionError",
            "RegisterReadError",
            "RegisterWriteError",
            "ValidationError",
            "ReadOnlyRegisterError",
            "HeatPumpStatus",
            "HeatingCircuitStatus",
            "OperatingMode",
            "OperatingType",
            "EnergyMode",
            "SeasonSelection",
            "ExternalHeatGeneratorMode",
            "ExternalHeatGeneratorStatus",
            "BooleanValue",
        }

        assert set(__all__) == expected
