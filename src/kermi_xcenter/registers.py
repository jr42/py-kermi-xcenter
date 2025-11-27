"""Modbus register definitions for Kermi heat pump modules.

This module defines all registers for the three Kermi Modbus modules:
- HeatPump (Unit 40): Main heat pump control
- StorageSystem (Units 50/51): Heating and hot water storage
- UniversalModule (Unit 30): Additional heating circuits

All register names are in English for code clarity, with German references
preserved in docstrings and the 'german_name' field.
"""

from collections.abc import Callable
from dataclasses import dataclass

from .types import RegisterAttribute
from .utils.conversions import (
    raw_to_cop,
    raw_to_flow_rate,
    raw_to_power,
    raw_to_temperature,
    temperature_to_raw,
)


@dataclass(frozen=True)
class RegisterDef:
    """Definition of a Modbus register.

    Attributes:
        address: Modbus register address
        name: English register name (used as attribute name)
        german_name: Original German name from Kermi documentation
        description: English description
        unit: Unit of measurement (°C, kW, l/min, h, etc.)
        attribute: Register attribute (R or R/W)
        code: Kermi sensor/parameter code (e.g., B14, BOT)
        data_type: Data type (int16, uint16, enum, bool)
        min_value: Minimum allowed value (for setpoint validation)
        max_value: Maximum allowed value (for setpoint validation)
        min_valid_value: Minimum physically valid sensor value (filters invalid data)
        max_valid_value: Maximum physically valid sensor value (filters invalid data)
        default: Default value
        enum_type: Enum class for enum registers
        converter: Function to convert raw value to engineering units
        inverse_converter: Function to convert engineering units to raw value
        scaling_factor: Scaling factor for manual conversion (deprecated, use converter)
    """

    address: int
    name: str
    german_name: str
    description: str
    unit: str
    attribute: RegisterAttribute
    code: str = ""
    data_type: str = "int16"
    min_value: float | None = None
    max_value: float | None = None
    min_valid_value: float | None = None
    max_valid_value: float | None = None
    default: float | None = None
    enum_type: type | None = None
    converter: Callable[[int], float | int] | None = None
    inverse_converter: Callable[[float], int] | None = None
    scaling_factor: float = 1.0

    @property
    def is_writable(self) -> bool:
        """Check if register is writable."""
        return "W" in self.attribute


# =============================================================================
# HEAT PUMP REGISTERS (Unit 40)
# =============================================================================

HEAT_PUMP_REGISTERS: dict[str, RegisterDef] = {
    # Energy source temperatures
    "energy_source_outlet": RegisterDef(
        address=1,
        name="energy_source_outlet",
        german_name="energiequelle_austritt",
        description="Energy source outlet temperature",
        unit="°C",
        attribute="R",
        code="B14",
        converter=raw_to_temperature,
    ),
    "energy_source_inlet": RegisterDef(
        address=2,
        name="energy_source_inlet",
        german_name="energiequelle_eintritt",
        description="Energy source inlet temperature",
        unit="°C",
        attribute="R",
        code="B15",
        converter=raw_to_temperature,
    ),
    "outdoor_temperature": RegisterDef(
        address=3,
        name="outdoor_temperature",
        german_name="aussentemperatur",
        description="Outdoor temperature sensor",
        unit="°C",
        attribute="R",
        code="BOT",
        converter=raw_to_temperature,
    ),
    # Heat pump circuit
    "supply_temp_heat_pump": RegisterDef(
        address=50,
        name="supply_temp_heat_pump",
        german_name="vorlauf_wp",
        description="Heat pump supply temperature",
        unit="°C",
        attribute="R",
        code="B16",
        converter=raw_to_temperature,
    ),
    "return_temp_heat_pump": RegisterDef(
        address=51,
        name="return_temp_heat_pump",
        german_name="ruecklauf_wp",
        description="Heat pump return temperature",
        unit="°C",
        attribute="R",
        code="B17",
        converter=raw_to_temperature,
    ),
    "flow_rate_heat_pump": RegisterDef(
        address=52,
        name="flow_rate_heat_pump",
        german_name="durchfluss_wp",
        description="Heat pump flow rate",
        unit="l/min",
        attribute="R",
        code="P13",
        converter=raw_to_flow_rate,
    ),
    # COP values
    "cop_total": RegisterDef(
        address=100,
        name="cop_total",
        german_name="cop_aktuell",
        description="Current COP total",
        unit="",
        attribute="R",
        data_type="uint16",
        converter=raw_to_cop,
    ),
    "cop_heating": RegisterDef(
        address=101,
        name="cop_heating",
        german_name="cop_heizen",
        description="Current COP heating",
        unit="",
        attribute="R",
        data_type="uint16",
        converter=raw_to_cop,
    ),
    "cop_hot_water": RegisterDef(
        address=102,
        name="cop_hot_water",
        german_name="cop_twe",
        description="Current COP hot water heating",
        unit="",
        attribute="R",
        data_type="uint16",
        converter=raw_to_cop,
    ),
    "cop_cooling": RegisterDef(
        address=103,
        name="cop_cooling",
        german_name="cop_kuehlen",
        description="Current COP cooling",
        unit="",
        attribute="R",
        data_type="uint16",
        converter=raw_to_cop,
    ),
    # Power values (thermal)
    "power_total": RegisterDef(
        address=104,
        name="power_total",
        german_name="leistung_aktuell",
        description="Current power total",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_heating": RegisterDef(
        address=105,
        name="power_heating",
        german_name="leistung_heizen",
        description="Current power heating",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_hot_water": RegisterDef(
        address=106,
        name="power_hot_water",
        german_name="leistung_twe",
        description="Current power hot water",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_cooling": RegisterDef(
        address=107,
        name="power_cooling",
        german_name="leistung_kuehlen",
        description="Current power cooling",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    # Power values (electrical)
    "power_electrical_total": RegisterDef(
        address=108,
        name="power_electrical_total",
        german_name="leistung_el_aktuell",
        description="Current electrical power total",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_electrical_heating": RegisterDef(
        address=109,
        name="power_electrical_heating",
        german_name="leistung_el_heizen",
        description="Current electrical power heating",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_electrical_hot_water": RegisterDef(
        address=110,
        name="power_electrical_hot_water",
        german_name="leistung_el_twe",
        description="Current electrical power hot water",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    "power_electrical_cooling": RegisterDef(
        address=111,
        name="power_electrical_cooling",
        german_name="leistung_el_kuehlen",
        description="Current electrical power cooling",
        unit="kW",
        attribute="R",
        data_type="uint16",
        converter=raw_to_power,
    ),
    # Operating hours
    "operating_hours_fan": RegisterDef(
        address=150,
        name="operating_hours_fan",
        german_name="bh_luefter",
        description="Operating hours fan",
        unit="h",
        attribute="R",
        data_type="uint16",
    ),
    "operating_hours_storage_pump": RegisterDef(
        address=151,
        name="operating_hours_storage_pump",
        german_name="bh_speicherladepumpe",
        description="Operating hours storage charging pump",
        unit="h",
        attribute="R",
        data_type="uint16",
    ),
    "operating_hours_compressor": RegisterDef(
        address=152,
        name="operating_hours_compressor",
        german_name="bh_verdichter",
        description="Operating hours compressor",
        unit="h",
        attribute="R",
        data_type="uint16",
    ),
    # Status
    "heat_pump_status": RegisterDef(
        address=200,
        name="heat_pump_status",
        german_name="status_waermepumpe",
        description="Heat pump status",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "global_alarm": RegisterDef(
        address=250,
        name="global_alarm",
        german_name="globaler_alarm",
        description="Global alarm",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    # PV modulation
    "pv_modulation_status": RegisterDef(
        address=300,
        name="pv_modulation_status",
        german_name="pv_modulation_status",
        description="PV modulation status",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    "pv_modulation_power": RegisterDef(
        address=301,
        name="pv_modulation_power",
        german_name="pv_modulation_leistung",
        description="PV modulation power",
        unit="W",
        attribute="R/W",
        data_type="uint16",
    ),
    "pv_modulation_setpoint_heating": RegisterDef(
        address=302,
        name="pv_modulation_setpoint_heating",
        german_name="pv_modulation_soll_hz",
        description="PV modulation setpoint heating circuit",
        unit="°C",
        attribute="R/W",
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "pv_modulation_setpoint_hot_water": RegisterDef(
        address=303,
        name="pv_modulation_setpoint_hot_water",
        german_name="pv_modulation_soll_twe",
        description="PV modulation setpoint hot water",
        unit="°C",
        attribute="R/W",
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
}

# =============================================================================
# STORAGE SYSTEM REGISTERS (Units 50 and 51)
# =============================================================================
# Note: Same register map for both heating storage (unit 50) and hot water storage (unit 51)

STORAGE_SYSTEM_REGISTERS: dict[str, RegisterDef] = {
    # Heating storage temperatures
    "heating_actual": RegisterDef(
        address=1,
        name="heating_actual",
        german_name="heizen_ist",
        description="Heating storage actual temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "heating_setpoint": RegisterDef(
        address=2,
        name="heating_setpoint",
        german_name="heizen_soll",
        description="Heating storage setpoint temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    # Cooling storage temperatures
    "cooling_actual": RegisterDef(
        address=50,
        name="cooling_actual",
        german_name="kuehlen_ist",
        description="Cooling storage actual temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "cooling_setpoint": RegisterDef(
        address=51,
        name="cooling_setpoint",
        german_name="kuehlen_soll",
        description="Cooling storage setpoint temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    # Hot water temperatures
    "hot_water_actual": RegisterDef(
        address=100,
        name="hot_water_actual",
        german_name="twe_ist",
        description="Hot water actual temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "hot_water_setpoint": RegisterDef(
        address=101,
        name="hot_water_setpoint",
        german_name="twe_soll",
        description="Hot water setpoint temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "hot_water_setpoint_constant": RegisterDef(
        address=102,
        name="hot_water_setpoint_constant",
        german_name="twe_soll_konstant",
        description="Constant hot water setpoint",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=85.0,
        default=48.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "hot_water_single_charge_active": RegisterDef(
        address=103,
        name="hot_water_single_charge_active",
        german_name="twe_einmalladung_aktiv",
        description="Hot water single charge active",
        unit="",
        attribute="R/W",
        data_type="bool",
        min_value=0.0,
        max_value=1.0,
        default=0.0,
    ),
    "hot_water_single_charge_setpoint": RegisterDef(
        address=104,
        name="hot_water_single_charge_setpoint",
        german_name="twe_einmalladung_soll",
        description="Hot water single charge setpoint",
        unit="°C",
        attribute="R/W",
        min_value=30.0,
        max_value=60.0,
        default=50.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    # Heating circuit
    "heating_circuit_status": RegisterDef(
        address=150,
        name="heating_circuit_status",
        german_name="heizkreis_status",
        description="Heating circuit status",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "heating_circuit_actual": RegisterDef(
        address=151,
        name="heating_circuit_actual",
        german_name="heizkreis_ist",
        description="Heating circuit actual temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "heating_circuit_setpoint": RegisterDef(
        address=152,
        name="heating_circuit_setpoint",
        german_name="heizkreis_soll",
        description="Heating circuit setpoint temperature (0-85°C)",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "heating_circuit_operating_mode": RegisterDef(
        address=153,
        name="heating_circuit_operating_mode",
        german_name="heizkreis_betriebsmodus",
        description="Heating circuit operating mode",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "heating_circuit_operating_type": RegisterDef(
        address=154,
        name="heating_circuit_operating_type",
        german_name="heizkreis_betriebsart",
        description="Heating circuit operating type",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    "heating_circuit_energy_mode": RegisterDef(
        address=155,
        name="heating_circuit_energy_mode",
        german_name="heizkreis_energiemodus",
        description="Heating circuit energy mode",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=2.0,
    ),
    "heating_curve_parallel_offset": RegisterDef(
        address=156,
        name="heating_curve_parallel_offset",
        german_name="heizkurve_parallelverschiebung",
        description="Heating curve parallel offset",
        unit="K",
        attribute="R/W",
        min_value=-5.0,
        max_value=5.0,
        default=0.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "season_selection_manual": RegisterDef(
        address=157,
        name="season_selection_manual",
        german_name="saisonauswahl_manuell",
        description="Manual season selection",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    "summer_mode_heating_off": RegisterDef(
        address=158,
        name="summer_mode_heating_off",
        german_name="sommerbetrieb_heizen_aus",
        description="Summer mode (heating off) threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=18.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "winter_mode_heating_on": RegisterDef(
        address=159,
        name="winter_mode_heating_on",
        german_name="winterbetrieb_heizen_ein",
        description="Winter mode (heating on) threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=16.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "cooling_mode_on": RegisterDef(
        address=160,
        name="cooling_mode_on",
        german_name="kuehlbetrieb_ein",
        description="Cooling mode on threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=22.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "cooling_mode_off": RegisterDef(
        address=161,
        name="cooling_mode_off",
        german_name="kuehlbetrieb_aus",
        description="Cooling mode off threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=20.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "summer_mode_active": RegisterDef(
        address=162,
        name="summer_mode_active",
        german_name="sommerbetrieb_aktiv",
        description="Summer mode active",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    "cooling_mode_active": RegisterDef(
        address=163,
        name="cooling_mode_active",
        german_name="kuehlbetrieb_aktiv",
        description="Cooling mode active",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    # External heat generator
    "external_heat_gen_status_heating": RegisterDef(
        address=200,
        name="external_heat_gen_status_heating",
        german_name="status_ext_wez_heizen",
        description="External heat generator status heating",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "external_heat_gen_mode_heating": RegisterDef(
        address=201,
        name="external_heat_gen_mode_heating",
        german_name="betriebsart_ext_wez_heizen",
        description="External heat generator mode heating",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    "external_heat_gen_status_hot_water": RegisterDef(
        address=202,
        name="external_heat_gen_status_hot_water",
        german_name="status_ext_wez_twe",
        description="External heat generator status hot water",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "external_heat_gen_mode_hot_water": RegisterDef(
        address=203,
        name="external_heat_gen_mode_hot_water",
        german_name="betriebsart_ext_wez_twe",
        description="External heat generator mode hot water",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    # Temperature sensors
    "t1_temperature": RegisterDef(
        address=250,
        name="t1_temperature",
        german_name="t1_temp",
        description="T1 (X13) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t2_temperature": RegisterDef(
        address=251,
        name="t2_temperature",
        german_name="t2_temp",
        description="T2 (X12) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t3_temperature": RegisterDef(
        address=252,
        name="t3_temperature",
        german_name="t3_temp",
        description="T3 (X11) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t4_temperature": RegisterDef(
        address=253,
        name="t4_temperature",
        german_name="t4_temp",
        description="T4 (X10) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "outdoor_temperature": RegisterDef(
        address=254,
        name="outdoor_temperature",
        german_name="aussentemperatur",
        description="Outdoor temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "outdoor_temperature_avg": RegisterDef(
        address=255,
        name="outdoor_temperature_avg",
        german_name="aussentemperatur_gemittelt",
        description="Average outdoor temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    # Operating hours
    "operating_hours_circuit_pump": RegisterDef(
        address=300,
        name="operating_hours_circuit_pump",
        german_name="bh_heizkreispumpe",
        description="Heating circuit pump operating hours",
        unit="h",
        attribute="R",
        data_type="uint16",
        min_value=0.0,
        max_value=65535.0,
    ),
    "operating_hours_external_heat_gen": RegisterDef(
        address=301,
        name="operating_hours_external_heat_gen",
        german_name="bh_ext_wez",
        description="External heat generator operating hours",
        unit="h",
        attribute="R",
        data_type="uint16",
        min_value=0.0,
        max_value=65535.0,
    ),
}


# =============================================================================
# UNIVERSAL MODULE REGISTERS (Unit 30)
# =============================================================================

UNIVERSAL_MODULE_REGISTERS: dict[str, RegisterDef] = {
    # Heating circuit
    "heating_circuit_status": RegisterDef(
        address=150,
        name="heating_circuit_status",
        german_name="heizkreis_status",
        description="Heating circuit status",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "heating_circuit_actual": RegisterDef(
        address=151,
        name="heating_circuit_actual",
        german_name="heizkreis_ist",
        description="Heating circuit actual temperature",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "heating_circuit_setpoint": RegisterDef(
        address=152,
        name="heating_circuit_setpoint",
        german_name="heizkreis_soll",
        description="Heating circuit setpoint temperature (0-85°C)",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "operating_mode": RegisterDef(
        address=153,
        name="operating_mode",
        german_name="betriebsmodus",
        description="Operating mode",
        unit="",
        attribute="R",
        data_type="enum",
    ),
    "operating_type": RegisterDef(
        address=154,
        name="operating_type",
        german_name="betriebsart",
        description="Operating type",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    "energy_mode": RegisterDef(
        address=155,
        name="energy_mode",
        german_name="energiemodus",
        description="Energy mode",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=2.0,
    ),
    "heating_curve_parallel_offset": RegisterDef(
        address=156,
        name="heating_curve_parallel_offset",
        german_name="heizkurve_parallelverschiebung",
        description="Heating curve parallel offset",
        unit="K",
        attribute="R/W",
        min_value=-5.0,
        max_value=5.0,
        default=0.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "season_selection_manual": RegisterDef(
        address=157,
        name="season_selection_manual",
        german_name="saisonauswahl_manuell",
        description="Manual season selection",
        unit="",
        attribute="R/W",
        data_type="enum",
        default=0.0,
    ),
    "summer_mode_heating_off": RegisterDef(
        address=158,
        name="summer_mode_heating_off",
        german_name="sommerbetrieb_heizen_aus",
        description="Summer mode (heating off) threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=18.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "winter_mode_heating_on": RegisterDef(
        address=159,
        name="winter_mode_heating_on",
        german_name="winterbetrieb_heizen_ein",
        description="Winter mode (heating on) threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=16.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "cooling_mode_on": RegisterDef(
        address=160,
        name="cooling_mode_on",
        german_name="kuehlbetrieb_ein",
        description="Cooling mode on threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=22.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "cooling_mode_off": RegisterDef(
        address=161,
        name="cooling_mode_off",
        german_name="kuehlbetrieb_aus",
        description="Cooling mode off threshold",
        unit="°C",
        attribute="R/W",
        min_value=0.0,
        max_value=50.0,
        default=20.0,
        converter=raw_to_temperature,
        inverse_converter=temperature_to_raw,
    ),
    "summer_mode_active": RegisterDef(
        address=162,
        name="summer_mode_active",
        german_name="sommerbetrieb_aktiv",
        description="Summer mode active",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    "cooling_mode_active": RegisterDef(
        address=163,
        name="cooling_mode_active",
        german_name="kuehlbetrieb_aktiv",
        description="Cooling mode active",
        unit="",
        attribute="R",
        data_type="bool",
    ),
    # Temperature sensors
    "t1_temperature": RegisterDef(
        address=250,
        name="t1_temperature",
        german_name="t1_temp",
        description="T1 (X9) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t2_temperature": RegisterDef(
        address=251,
        name="t2_temperature",
        german_name="t2_temp",
        description="T2 (X10) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t3_temperature": RegisterDef(
        address=252,
        name="t3_temperature",
        german_name="t3_temp",
        description="T3 (X11) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    "t4_temperature": RegisterDef(
        address=253,
        name="t4_temperature",
        german_name="t4_temp",
        description="T4 (X12) temperature sensor",
        unit="°C",
        attribute="R",
        converter=raw_to_temperature,
    ),
    # Operating hours
    "operating_hours_circuit_pump": RegisterDef(
        address=300,
        name="operating_hours_circuit_pump",
        german_name="bh_heizkreispumpe",
        description="Heating circuit pump operating hours",
        unit="h",
        attribute="R",
        data_type="uint16",
        min_value=0.0,
        max_value=65535.0,
    ),
}
