"""Type definitions and enums for Kermi Modbus devices.

This module defines all enum types used across different Kermi modules.
English names are used for code clarity, with German equivalents noted
in docstrings.
"""

from enum import IntEnum
from typing import Literal

# Type aliases for clarity
ModbusAddress = int
UnitId = int
RegisterValue = int
Temperature = float  # Always in °C
Power = float  # Always in kW
FlowRate = float  # Always in l/min


class HeatPumpStatus(IntEnum):
    """Heat pump operating status (Wärmepumpe Status).

    Register: 200 (Unit 40)
    German: Status Wärmepumpe
    """

    STANDBY = 0  # Standby
    ALARM = 1  # Alarm
    HOT_WATER = 2  # TWE (Trinkwassererwärmung)
    COOLING = 3  # Kühlen
    HEATING = 4  # Heizen
    DEFROST = 5  # Abtauung
    PREPARATION = 6  # Vorbereitung
    BLOCKED = 7  # Blockiert
    UTILITY_LOCK = 8  # EVU Sperre
    NOT_AVAILABLE = 9  # nicht verfügbar


class HeatingCircuitStatus(IntEnum):
    """Heating circuit status (Heizkreis Status).

    Used in both StorageSystem and UniversalModule.
    Register: 150 (Units 30, 50, 51)
    German: Status Heizkreis
    """

    OFF = 0  # Aus
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen
    DEW_POINT = 3  # Taupunkt
    PUMP_MAINTENANCE = 4  # Pumpenwartungslauf
    FROST_PROTECTION = 5  # Frostschutz
    MANUAL_MODE = 6  # Handbetrieb
    TEST_MODE = 7  # Testmodus
    INITIALIZING = 8  # Initialisierung
    SAFETY_STATE = 9  # Sicherheitszustand


class OperatingMode(IntEnum):
    """Operating mode (Betriebsmodus).

    Actual mode the system is currently in (read-only).
    Register: 153 (Units 30, 50, 51)
    German: Betriebsmodus
    """

    OFF = 0  # Aus
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen


class OperatingType(IntEnum):
    """Operating type/mode selection (Betriebsart).

    User-selectable operating type.
    Register: 154 (Units 30, 50, 51)
    German: Betriebsart
    """

    AUTO = 0  # Auto
    HEATING = 1  # Heizen (StorageSystem) / Aus (UniversalModule)


class EnergyMode(IntEnum):
    """Energy mode setting (Energiemodus).

    Register: 155 (Units 30, 50, 51)
    German: Energiemodus
    """

    OFF = 0  # Off
    ECO = 1  # Eco
    NORMAL = 2  # Normal
    COMFORT = 3  # Comfort
    CUSTOM = 4  # Benutzerdefiniert


class SeasonSelection(IntEnum):
    """Manual season selection (Saisonauswahl manuell).

    Register: 157 (Units 30, 50, 51)
    German: Manuelle Saisonauswahl
    """

    AUTO = 0  # Auto
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen
    OFF = 3  # Aus


class ExternalHeatGeneratorMode(IntEnum):
    """External heat generator operating mode (Betriebsart ext. WEZ).

    Register: 201, 203 (Units 50, 51)
    German: Betriebsart externer Wärmeerzeuger
    """

    AUTO = 0  # Auto
    HEAT_PUMP_ONLY = 1  # Nur WP
    BOTH = 2  # Beide
    SECONDARY_ONLY = 3  # Sekundärer WEZ


class ExternalHeatGeneratorStatus(IntEnum):
    """External heat generator status codes (Status ext. WEZ).

    Register: 200, 202 (Units 50, 51)
    German: Status externer Wärmeerzeuger
    """

    NO_REQUEST = 0  # keine Anforderung
    REQUEST = 100  # Anforderung
    READY_AUTO_PARALLEL = 200  # Bereitschaft Auto Parallel
    READY_AUTO_ALTERNATIVE = 201  # Bereitschaft Auto Alternativ
    READY_FAULT = 204  # Bereitschaft wg. Störung
    READY_MANUAL_PARALLEL = 205  # Bereitschaft Handbetrieb Parallel
    READY_DUE_TO_MANUAL_PARALLEL = 206  # Bereitschaft wg. Handbetrieb Parallel
    READY_UTILITY_LOCK = 207  # Bereitschaft EVU Sperre
    REQUEST_AUTO_PARALLEL = 300  # Anforderung Auto Parallel
    REQUEST_AUTO_ALTERNATIVE = 301  # Anforderung Auto Alternativ
    REQUEST_FAULT = 304  # Anforderung wg. Störung
    REQUEST_MANUAL_PARALLEL = 305  # Anforderung Handbetrieb Parallel
    REQUEST_DUE_TO_MANUAL_PARALLEL = 306  # Anforderung wg. Handbetrieb Parallel
    REQUEST_UTILITY_LOCK = 307  # Anforderung EVU Sperre


class BooleanValue(IntEnum):
    """Boolean value representation for on/off registers."""

    NO = 0  # Nein / Aus / Off
    YES = 1  # Ja / Ein / On


# Attribute type for register access
RegisterAttribute = Literal["R", "R/W"]
