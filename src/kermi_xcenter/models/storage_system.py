"""Storage system module (Speichersystemmodul) - Units 50 and 51."""

from ..client import KermiModbusClient
from ..registers import STORAGE_SYSTEM_REGISTERS
from ..types import (
    EnergyMode,
    ExternalHeatGeneratorMode,
    ExternalHeatGeneratorStatus,
    HeatingCircuitStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)
from .base import KermiDevice


class StorageSystem(KermiDevice):
    """Kermi storage system module (Speichersystemmodul).

    Unit IDs:
    - 50: Heating storage
    - 51: Hot water (TWE) storage

    Note: Both units use the same register map.

    Provides access to:
    - Heating and cooling storage temperatures
    - Hot water temperatures and settings
    - Heating circuit control and status
    - Season selection and operating modes
    - External heat generator control
    - Temperature sensors
    - Operating hours

    Example:
        >>> client = KermiModbusClient(host="192.168.1.100")
        >>> heating_storage = StorageSystem(client, unit_id=50)
        >>> hot_water_storage = StorageSystem(client, unit_id=51)
        >>>
        >>> async with client:
        ...     temp = await heating_storage.get_heating_actual()
        ...     await hot_water_storage.set_hot_water_setpoint_constant(50.0)
    """

    def __init__(
        self,
        client: KermiModbusClient,
        unit_id: int = 50,
        capabilities: dict[str, bool] | None = None,
    ) -> None:
        """Initialize storage system device.

        Args:
            client: Modbus client instance
            unit_id: Modbus unit ID (50 for heating, 51 for hot water)
            capabilities: Optional pre-discovered capabilities to skip unavailable registers
        """
        super().__init__(client, unit_id, STORAGE_SYSTEM_REGISTERS, capabilities)

    # Heating storage temperatures

    async def get_heating_actual(self) -> float | None:
        """Get heating storage actual temperature in °C.

        Register: 1
        German: Isttemperatur Heizspeicher
        """
        return await self._read_register(self.registers["heating_actual"])

    async def get_heating_setpoint(self) -> float | None:
        """Get heating storage setpoint temperature in °C.

        Register: 2
        German: Solltemperatur Heizspeicher
        """
        return await self._read_register(self.registers["heating_setpoint"])

    # Cooling storage temperatures

    async def get_cooling_actual(self) -> float | None:
        """Get cooling storage actual temperature in °C.

        Register: 50
        German: Isttemperatur Kühlspeicher
        """
        return await self._read_register(self.registers["cooling_actual"])

    async def get_cooling_setpoint(self) -> float | None:
        """Get cooling storage setpoint temperature in °C.

        Register: 51
        German: Solltemperatur Kühlspeicher
        """
        return await self._read_register(self.registers["cooling_setpoint"])

    # Hot water temperatures

    async def get_hot_water_actual(self) -> float | None:
        """Get hot water actual temperature in °C.

        Register: 100
        German: Isttemperatur TWE
        """
        return await self._read_register(self.registers["hot_water_actual"])

    async def get_hot_water_setpoint(self) -> float | None:
        """Get hot water setpoint temperature in °C.

        Register: 101
        German: Solltemperatur TWE
        """
        return await self._read_register(self.registers["hot_water_setpoint"])

    async def get_hot_water_setpoint_constant(self) -> float | None:
        """Get constant hot water setpoint in °C.

        Register: 102
        German: Konstanter Sollwert TWE
        Range: 0-85°C, Default: 48°C
        """
        return await self._read_register(self.registers["hot_water_setpoint_constant"])

    async def set_hot_water_setpoint_constant(self, temp: float) -> None:
        """Set constant hot water setpoint in °C.

        Register: 102 (R/W)
        German: Konstanter Sollwert TWE

        Args:
            temp: Temperature in °C (0-85°C)
        """
        await self._write_register(self.registers["hot_water_setpoint_constant"], temp)

    async def get_hot_water_single_charge_active(self) -> bool | None:
        """Get hot water single charge activation status.

        Register: 103
        German: Einmalladung TWE
        """
        value = await self._read_register(self.registers["hot_water_single_charge_active"])
        return bool(value) if value is not None else None

    async def set_hot_water_single_charge_active(self, active: bool) -> None:
        """Activate or deactivate hot water single charge.

        Register: 103 (R/W)
        German: Einmalladung TWE

        Args:
            active: True to activate, False to deactivate
        """
        await self._write_register(self.registers["hot_water_single_charge_active"], int(active))

    async def get_hot_water_single_charge_setpoint(self) -> float | None:
        """Get hot water single charge setpoint in °C.

        Register: 104
        German: Sollwert Einmalladung TWE
        Range: 30-60°C, Default: 50°C
        """
        return await self._read_register(self.registers["hot_water_single_charge_setpoint"])

    async def set_hot_water_single_charge_setpoint(self, temp: float) -> None:
        """Set hot water single charge setpoint in °C.

        Register: 104 (R/W)
        German: Sollwert Einmalladung TWE

        Args:
            temp: Temperature in °C (30-60°C)
        """
        await self._write_register(self.registers["hot_water_single_charge_setpoint"], temp)

    # Heating circuit

    async def get_heating_circuit_status(self) -> HeatingCircuitStatus | None:
        """Get heating circuit status.

        Register: 150
        German: Status Heizkreis

        Returns:
            HeatingCircuitStatus enum value
        """
        value = await self._read_register(self.registers["heating_circuit_status"])
        return HeatingCircuitStatus(int(value)) if value is not None else None

    async def get_heating_circuit_actual(self) -> float | None:
        """Get heating circuit actual temperature in °C.

        Register: 151
        German: Isttemperatur Heizkreis
        """
        return await self._read_register(self.registers["heating_circuit_actual"])

    async def get_heating_circuit_setpoint(self) -> float | None:
        """Get heating circuit setpoint temperature in °C.

        Register: 152
        German: Solltemperatur Heizkreis
        Range: 0-85°C
        """
        return await self._read_register(self.registers["heating_circuit_setpoint"])

    async def get_heating_circuit_operating_mode(self) -> OperatingMode | None:
        """Get heating circuit operating mode (current actual mode).

        Register: 153
        German: Betriebsmodus

        Returns:
            OperatingMode enum value (OFF, HEATING, COOLING)
        """
        value = await self._read_register(self.registers["heating_circuit_operating_mode"])
        return OperatingMode(int(value)) if value is not None else None

    async def get_heating_circuit_operating_type(self) -> OperatingType | None:
        """Get heating circuit operating type (user selection).

        Register: 154
        German: Betriebsart

        Returns:
            OperatingType enum value (AUTO, HEATING)
        """
        value = await self._read_register(self.registers["heating_circuit_operating_type"])
        return OperatingType(int(value)) if value is not None else None

    async def set_heating_circuit_operating_type(self, mode: OperatingType) -> None:
        """Set heating circuit operating type.

        Register: 154 (R/W)
        German: Betriebsart

        Args:
            mode: OperatingType enum value (AUTO or HEATING)
        """
        await self._write_register(self.registers["heating_circuit_operating_type"], mode.value)

    async def get_heating_circuit_energy_mode(self) -> EnergyMode | None:
        """Get heating circuit energy mode.

        Register: 155
        German: Energiemodus

        Returns:
            EnergyMode enum value
        """
        value = await self._read_register(self.registers["heating_circuit_energy_mode"])
        return EnergyMode(int(value)) if value is not None else None

    async def set_heating_circuit_energy_mode(self, mode: EnergyMode) -> None:
        """Set heating circuit energy mode.

        Register: 155 (R/W)
        German: Energiemodus

        Args:
            mode: EnergyMode enum value (OFF, ECO, NORMAL, COMFORT, CUSTOM)
        """
        await self._write_register(self.registers["heating_circuit_energy_mode"], mode.value)

    async def get_heating_curve_parallel_offset(self) -> float | None:
        """Get heating curve parallel offset in K.

        Register: 156
        German: Parallelverschiebung Heizkurve
        Range: -5 to +5K
        """
        return await self._read_register(self.registers["heating_curve_parallel_offset"])

    async def set_heating_curve_parallel_offset(self, offset: float) -> None:
        """Set heating curve parallel offset in K.

        Register: 156 (R/W)
        German: Parallelverschiebung Heizkurve

        Args:
            offset: Offset in Kelvin (-5 to +5K)
        """
        await self._write_register(self.registers["heating_curve_parallel_offset"], offset)

    async def get_season_selection_manual(self) -> SeasonSelection | None:
        """Get manual season selection.

        Register: 157
        German: Manuelle Saisonauswahl

        Returns:
            SeasonSelection enum value
        """
        value = await self._read_register(self.registers["season_selection_manual"])
        return SeasonSelection(int(value)) if value is not None else None

    async def set_season_selection_manual(self, selection: SeasonSelection) -> None:
        """Set manual season selection.

        Register: 157 (R/W)
        German: Manuelle Saisonauswahl

        Args:
            selection: SeasonSelection enum value (AUTO, HEATING, COOLING, OFF)
        """
        await self._write_register(self.registers["season_selection_manual"], selection.value)

    # Season thresholds

    async def get_summer_mode_heating_off(self) -> float | None:
        """Get summer mode (heating off) threshold in °C.

        Register: 158
        German: Sommerbetrieb (Heizen Aus)
        Range: 0-50°C, Default: 18°C
        """
        return await self._read_register(self.registers["summer_mode_heating_off"])

    async def set_summer_mode_heating_off(self, temp: float) -> None:
        """Set summer mode (heating off) threshold in °C.

        Register: 158 (R/W)

        Args:
            temp: Temperature threshold in °C (0-50°C)
        """
        await self._write_register(self.registers["summer_mode_heating_off"], temp)

    async def get_winter_mode_heating_on(self) -> float | None:
        """Get winter mode (heating on) threshold in °C.

        Register: 159
        German: Winterbetrieb (Heizen Ein)
        Range: 0-50°C, Default: 16°C
        """
        return await self._read_register(self.registers["winter_mode_heating_on"])

    async def set_winter_mode_heating_on(self, temp: float) -> None:
        """Set winter mode (heating on) threshold in °C.

        Register: 159 (R/W)

        Args:
            temp: Temperature threshold in °C (0-50°C)
        """
        await self._write_register(self.registers["winter_mode_heating_on"], temp)

    async def get_cooling_mode_on(self) -> float | None:
        """Get cooling mode on threshold in °C.

        Register: 160
        German: Kühlbetrieb Ein
        Range: 0-50°C, Default: 22°C
        """
        return await self._read_register(self.registers["cooling_mode_on"])

    async def set_cooling_mode_on(self, temp: float) -> None:
        """Set cooling mode on threshold in °C.

        Register: 160 (R/W)

        Args:
            temp: Temperature threshold in °C (0-50°C)
        """
        await self._write_register(self.registers["cooling_mode_on"], temp)

    async def get_cooling_mode_off(self) -> float | None:
        """Get cooling mode off threshold in °C.

        Register: 161
        German: Kühlbetrieb Aus
        Range: 0-50°C, Default: 20°C
        """
        return await self._read_register(self.registers["cooling_mode_off"])

    async def set_cooling_mode_off(self, temp: float) -> None:
        """Set cooling mode off threshold in °C.

        Register: 161 (R/W)

        Args:
            temp: Temperature threshold in °C (0-50°C)
        """
        await self._write_register(self.registers["cooling_mode_off"], temp)

    async def get_summer_mode_active(self) -> bool | None:
        """Get summer mode active status.

        Register: 162
        German: Sommerbetrieb aktiv
        """
        value = await self._read_register(self.registers["summer_mode_active"])
        return bool(value) if value is not None else None

    async def get_cooling_mode_active(self) -> bool | None:
        """Get cooling mode active status.

        Register: 163
        German: Kühlbetrieb aktiv
        """
        value = await self._read_register(self.registers["cooling_mode_active"])
        return bool(value) if value is not None else None

    # External heat generator

    async def get_external_heat_gen_status_heating(self) -> ExternalHeatGeneratorStatus | None:
        """Get external heat generator status for heating.

        Register: 200
        German: Status externer Wärmeerzeuger Heizen

        Returns:
            ExternalHeatGeneratorStatus enum value
        """
        value = await self._read_register(self.registers["external_heat_gen_status_heating"])
        return ExternalHeatGeneratorStatus(int(value)) if value is not None else None

    async def get_external_heat_gen_mode_heating(self) -> ExternalHeatGeneratorMode | None:
        """Get external heat generator mode for heating.

        Register: 201
        German: Betriebsart ext. WEZ Heizen

        Returns:
            ExternalHeatGeneratorMode enum value
        """
        value = await self._read_register(self.registers["external_heat_gen_mode_heating"])
        return ExternalHeatGeneratorMode(int(value)) if value is not None else None

    async def set_external_heat_gen_mode_heating(self, mode: ExternalHeatGeneratorMode) -> None:
        """Set external heat generator mode for heating.

        Register: 201 (R/W)

        Args:
            mode: ExternalHeatGeneratorMode enum value
        """
        await self._write_register(self.registers["external_heat_gen_mode_heating"], mode.value)

    async def get_external_heat_gen_status_hot_water(self) -> ExternalHeatGeneratorStatus | None:
        """Get external heat generator status for hot water.

        Register: 202
        German: Status externer Wärmeerzeuger TWE

        Returns:
            ExternalHeatGeneratorStatus enum value
        """
        value = await self._read_register(self.registers["external_heat_gen_status_hot_water"])
        return ExternalHeatGeneratorStatus(int(value)) if value is not None else None

    async def get_external_heat_gen_mode_hot_water(self) -> ExternalHeatGeneratorMode | None:
        """Get external heat generator mode for hot water.

        Register: 203
        German: Betriebsart ext. WEZ TWE

        Returns:
            ExternalHeatGeneratorMode enum value
        """
        value = await self._read_register(self.registers["external_heat_gen_mode_hot_water"])
        return ExternalHeatGeneratorMode(int(value)) if value is not None else None

    async def set_external_heat_gen_mode_hot_water(self, mode: ExternalHeatGeneratorMode) -> None:
        """Set external heat generator mode for hot water.

        Register: 203 (R/W)

        Args:
            mode: ExternalHeatGeneratorMode enum value
        """
        await self._write_register(self.registers["external_heat_gen_mode_hot_water"], mode.value)

    # Temperature sensors

    async def get_t1_temperature(self) -> float | None:
        """Get T1 (X13) temperature sensor reading in °C.

        Register: 250
        German: T1 (X13) Temperaturfühler
        """
        return await self._read_register(self.registers["t1_temperature"])

    async def get_t2_temperature(self) -> float | None:
        """Get T2 (X12) temperature sensor reading in °C.

        Register: 251
        German: T2 (X12) Temperaturfühler
        """
        return await self._read_register(self.registers["t2_temperature"])

    async def get_t3_temperature(self) -> float | None:
        """Get T3 (X11) temperature sensor reading in °C.

        Register: 252
        German: T3 (X11) Temperaturfühler
        """
        return await self._read_register(self.registers["t3_temperature"])

    async def get_t4_temperature(self) -> float | None:
        """Get T4 (X10) temperature sensor reading in °C.

        Register: 253
        German: T4 (X10) Temperaturfühler
        """
        return await self._read_register(self.registers["t4_temperature"])

    async def get_outdoor_temperature(self) -> float | None:
        """Get outdoor temperature in °C.

        Register: 254
        German: Außentemperatur
        """
        return await self._read_register(self.registers["outdoor_temperature"])

    async def get_outdoor_temperature_avg(self) -> float | None:
        """Get average outdoor temperature in °C.

        Register: 255
        German: Gemittelte Außentemperatur
        """
        return await self._read_register(self.registers["outdoor_temperature_avg"])

    # Operating hours

    async def get_operating_hours_circuit_pump(self) -> int | None:
        """Get heating circuit pump operating hours.

        Register: 300
        German: Heizkreispumpe Laufzeit
        """
        value = await self._read_register(self.registers["operating_hours_circuit_pump"])
        return int(value) if value is not None else None

    async def get_operating_hours_external_heat_gen(self) -> int | None:
        """Get external heat generator operating hours.

        Register: 301
        German: Externer Wärmeerzeuger Laufzeit
        """
        value = await self._read_register(self.registers["operating_hours_external_heat_gen"])
        return int(value) if value is not None else None
