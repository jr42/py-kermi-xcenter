"""Universal module (Universalmodul) - Unit ID 30."""

from ..client import KermiModbusClient
from ..registers import UNIVERSAL_MODULE_REGISTERS
from ..types import EnergyMode, HeatingCircuitStatus, OperatingMode, OperatingType, SeasonSelection
from .base import KermiDevice


class UniversalModule(KermiDevice):
    """Kermi universal module (Universalmodul).

    Unit ID: 30

    Provides access to additional heating circuits with:
    - Heating circuit control and status
    - Operating modes and energy settings
    - Season selection
    - Temperature sensors
    - Operating hours

    Example:
        >>> client = KermiModbusClient(host="192.168.1.100")
        >>> universal = UniversalModule(client)
        >>>
        >>> async with client:
        ...     status = await universal.get_heating_circuit_status()
        ...     temp = await universal.get_heating_circuit_actual()
        ...     await universal.set_energy_mode(EnergyMode.ECO)
    """

    def __init__(
        self,
        client: KermiModbusClient,
        unit_id: int = 30,
        capabilities: dict[str, bool] | None = None,
    ) -> None:
        """Initialize universal module device.

        Args:
            client: Modbus client instance
            unit_id: Modbus unit ID (default: 30)
            capabilities: Optional pre-discovered capabilities to skip unavailable registers
        """
        super().__init__(client, unit_id, UNIVERSAL_MODULE_REGISTERS, capabilities)

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

    async def get_operating_mode(self) -> OperatingMode | None:
        """Get operating mode (current actual mode).

        Register: 153
        German: Betriebsmodus

        Returns:
            OperatingMode enum value (OFF, HEATING, COOLING)
        """
        value = await self._read_register(self.registers["operating_mode"])
        return OperatingMode(int(value)) if value is not None else None

    async def get_operating_type(self) -> OperatingType | None:
        """Get operating type (user selection).

        Register: 154
        German: Betriebsart

        Returns:
            OperatingType enum value (AUTO, OFF)
        """
        value = await self._read_register(self.registers["operating_type"])
        return OperatingType(int(value)) if value is not None else None

    async def set_operating_type(self, mode: OperatingType) -> None:
        """Set operating type.

        Register: 154 (R/W)
        German: Betriebsart

        Args:
            mode: OperatingType enum value (AUTO or OFF for universal module)
        """
        await self._write_register(self.registers["operating_type"], mode.value)

    async def get_energy_mode(self) -> EnergyMode | None:
        """Get energy mode.

        Register: 155
        German: Energiemodus

        Returns:
            EnergyMode enum value
        """
        value = await self._read_register(self.registers["energy_mode"])
        return EnergyMode(int(value)) if value is not None else None

    async def set_energy_mode(self, mode: EnergyMode) -> None:
        """Set energy mode.

        Register: 155 (R/W)
        German: Energiemodus

        Args:
            mode: EnergyMode enum value (OFF, ECO, NORMAL, COMFORT, CUSTOM)
        """
        await self._write_register(self.registers["energy_mode"], mode.value)

    async def get_heating_curve_parallel_offset(self) -> float | None:
        """Get heating curve parallel offset in K.

        Register: 156
        German: Parallelverschiebung Kurve
        Range: -5 to +5K
        """
        return await self._read_register(self.registers["heating_curve_parallel_offset"])

    async def set_heating_curve_parallel_offset(self, offset: float) -> None:
        """Set heating curve parallel offset in K.

        Register: 156 (R/W)
        German: Parallelverschiebung Kurve

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

    # Temperature sensors

    async def get_t1_temperature(self) -> float | None:
        """Get T1 (X9) temperature sensor reading in °C.

        Register: 250
        German: T1 (X9) Temperaturfühler
        """
        return await self._read_register(self.registers["t1_temperature"])

    async def get_t2_temperature(self) -> float | None:
        """Get T2 (X10) temperature sensor reading in °C.

        Register: 251
        German: T2 (X10) Temperaturfühler
        """
        return await self._read_register(self.registers["t2_temperature"])

    async def get_t3_temperature(self) -> float | None:
        """Get T3 (X11) temperature sensor reading in °C.

        Register: 252
        German: T3 (X11) Temperaturfühler
        """
        return await self._read_register(self.registers["t3_temperature"])

    async def get_t4_temperature(self) -> float | None:
        """Get T4 (X12) temperature sensor reading in °C.

        Register: 253
        German: T4 (X12) Temperaturfühler
        """
        return await self._read_register(self.registers["t4_temperature"])

    # Operating hours

    async def get_operating_hours_circuit_pump(self) -> int | None:
        """Get heating circuit pump operating hours.

        Register: 300
        German: Heizkreispumpe Laufzeit
        """
        value = await self._read_register(self.registers["operating_hours_circuit_pump"])
        return int(value) if value is not None else None
