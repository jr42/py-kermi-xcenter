"""Heat pump device module (Wärmepumpe) - Unit ID 40."""

from ..client import KermiModbusClient
from ..registers import HEAT_PUMP_REGISTERS
from ..types import HeatPumpStatus
from .base import KermiDevice


class HeatPump(KermiDevice):
    """Kermi heat pump device (Wärmepumpe).

    Unit ID: 40

    Provides access to all heat pump registers including:
    - Energy source temperatures
    - Heat pump circuit temperatures and flow
    - COP (Coefficient of Performance) values
    - Power measurements (thermal and electrical)
    - Operating hours counters
    - Status and alarms
    - PV modulation controls

    Example:
        >>> client = KermiModbusClient(host="192.168.1.100")
        >>> heat_pump = HeatPump(client)
        >>>
        >>> async with client:
        ...     temp = await heat_pump.get_outdoor_temperature()
        ...     cop = await heat_pump.get_cop_total()
        ...     status = await heat_pump.get_heat_pump_status()
        ...     print(f"Outdoor: {temp}°C, COP: {cop}, Status: {status.name}")
    """

    def __init__(self, client: KermiModbusClient, unit_id: int = 40) -> None:
        """Initialize heat pump device.

        Args:
            client: Modbus client instance
            unit_id: Modbus unit ID (default: 40)
        """
        super().__init__(client, unit_id, HEAT_PUMP_REGISTERS)

    # Energy source temperatures

    async def get_energy_source_outlet(self) -> float:
        """Get energy source outlet temperature in °C.

        Kermi code: B14, Register: 1
        German: Energiequelle Austrittstemperatur
        """
        return await self._read_register(self.registers["energy_source_outlet"])

    async def get_energy_source_inlet(self) -> float:
        """Get energy source inlet temperature in °C.

        Kermi code: B15, Register: 2
        German: Energiequelle Eintrittstemperatur
        """
        return await self._read_register(self.registers["energy_source_inlet"])

    async def get_outdoor_temperature(self) -> float:
        """Get outdoor temperature in °C.

        Kermi code: BOT, Register: 3
        German: Außentemperaturfühler
        """
        return await self._read_register(self.registers["outdoor_temperature"])

    # Heat pump circuit

    async def get_supply_temp_heat_pump(self) -> float:
        """Get heat pump supply temperature in °C.

        Kermi code: B16, Register: 50
        German: Vorlauftemperatur Wärmepumpe
        """
        return await self._read_register(self.registers["supply_temp_heat_pump"])

    async def get_return_temp_heat_pump(self) -> float:
        """Get heat pump return temperature in °C.

        Kermi code: B17, Register: 51
        German: Rücklauftemperatur Wärmepumpe
        """
        return await self._read_register(self.registers["return_temp_heat_pump"])

    async def get_flow_rate_heat_pump(self) -> float:
        """Get heat pump flow rate in l/min.

        Kermi code: P13, Register: 52
        German: Durchfluss Wärmepumpe
        """
        return await self._read_register(self.registers["flow_rate_heat_pump"])

    # COP values

    async def get_cop_total(self) -> float:
        """Get current total COP (Coefficient of Performance).

        Register: 100
        German: Aktueller COP gesamt
        """
        return await self._read_register(self.registers["cop_total"])

    async def get_cop_heating(self) -> float:
        """Get current COP for heating mode.

        Register: 101
        German: Aktueller COP Heizen
        """
        return await self._read_register(self.registers["cop_heating"])

    async def get_cop_hot_water(self) -> float:
        """Get current COP for hot water heating.

        Register: 102
        German: Aktueller COP Trinkwassererwärmung
        """
        return await self._read_register(self.registers["cop_hot_water"])

    async def get_cop_cooling(self) -> float:
        """Get current COP for cooling mode.

        Register: 103
        German: Aktueller COP Kühlen
        """
        return await self._read_register(self.registers["cop_cooling"])

    # Thermal power

    async def get_power_total(self) -> float:
        """Get current total thermal power in kW.

        Register: 104
        German: Aktuelle Leistung gesamt
        """
        return await self._read_register(self.registers["power_total"])

    async def get_power_heating(self) -> float:
        """Get current heating power in kW.

        Register: 105
        German: Aktuelle Leistung Heizen
        """
        return await self._read_register(self.registers["power_heating"])

    async def get_power_hot_water(self) -> float:
        """Get current hot water heating power in kW.

        Register: 106
        German: Aktuelle Leistung TWE
        """
        return await self._read_register(self.registers["power_hot_water"])

    async def get_power_cooling(self) -> float:
        """Get current cooling power in kW.

        Register: 107
        German: Aktuelle Leistung Kühlen
        """
        return await self._read_register(self.registers["power_cooling"])

    # Electrical power

    async def get_power_electrical_total(self) -> float:
        """Get current total electrical power consumption in kW.

        Register: 108
        German: Aktuelle elektrische Leistung gesamt
        """
        return await self._read_register(self.registers["power_electrical_total"])

    async def get_power_electrical_heating(self) -> float:
        """Get current electrical power consumption for heating in kW.

        Register: 109
        German: Aktuelle elektrische Leistung Heizen
        """
        return await self._read_register(self.registers["power_electrical_heating"])

    async def get_power_electrical_hot_water(self) -> float:
        """Get current electrical power consumption for hot water in kW.

        Register: 110
        German: Aktuelle elektrische Leistung TWE
        """
        return await self._read_register(self.registers["power_electrical_hot_water"])

    async def get_power_electrical_cooling(self) -> float:
        """Get current electrical power consumption for cooling in kW.

        Register: 111
        German: Aktuelle elektrische Leistung Kühlen
        """
        return await self._read_register(self.registers["power_electrical_cooling"])

    # Operating hours

    async def get_operating_hours_fan(self) -> int:
        """Get fan operating hours.

        Register: 150
        German: Betriebsstunden Lüfter
        """
        return int(await self._read_register(self.registers["operating_hours_fan"]))

    async def get_operating_hours_storage_pump(self) -> int:
        """Get storage charging pump operating hours.

        Register: 151
        German: Betriebsstunden Speicherladepumpe
        """
        return int(await self._read_register(self.registers["operating_hours_storage_pump"]))

    async def get_operating_hours_compressor(self) -> int:
        """Get compressor operating hours.

        Register: 152
        German: Betriebsstunden Verdichter
        """
        return int(await self._read_register(self.registers["operating_hours_compressor"]))

    # Status and alarms

    async def get_heat_pump_status(self) -> HeatPumpStatus:
        """Get heat pump operating status.

        Register: 200
        German: Status Wärmepumpe

        Returns:
            HeatPumpStatus enum value (STANDBY, ALARM, HOT_WATER, COOLING, etc.)
        """
        value = await self._read_register(self.registers["heat_pump_status"])
        return HeatPumpStatus(int(value))

    async def get_global_alarm(self) -> bool:
        """Get global alarm status.

        Register: 250
        German: Globaler Alarm

        Returns:
            True if alarm is active, False otherwise
        """
        return bool(await self._read_register(self.registers["global_alarm"]))

    # PV modulation

    async def get_pv_modulation_status(self) -> bool:
        """Get PV modulation status.

        Register: 300
        German: Status PV Modulation Wärmepumpe

        Returns:
            True if PV modulation is active, False otherwise
        """
        return bool(await self._read_register(self.registers["pv_modulation_status"]))

    async def get_pv_modulation_power(self) -> int:
        """Get PV modulation power setting in Watts.

        Register: 301
        German: Aktuelle Leistung PV Modulation
        """
        return int(await self._read_register(self.registers["pv_modulation_power"]))

    async def set_pv_modulation_power(self, watts: int) -> None:
        """Set PV modulation power in Watts.

        Register: 301 (R/W)
        German: Aktuelle Leistung PV Modulation

        Args:
            watts: Power in Watts
        """
        await self._write_register(self.registers["pv_modulation_power"], watts)

    async def get_pv_modulation_setpoint_heating(self) -> float:
        """Get PV modulation heating circuit setpoint in °C.

        Register: 302
        German: Solltemperatur Heizkreis PV Modulation
        """
        return await self._read_register(self.registers["pv_modulation_setpoint_heating"])

    async def set_pv_modulation_setpoint_heating(self, temp: float) -> None:
        """Set PV modulation heating circuit setpoint in °C.

        Register: 302 (R/W)
        German: Solltemperatur Heizkreis PV Modulation

        Args:
            temp: Temperature setpoint in °C
        """
        await self._write_register(self.registers["pv_modulation_setpoint_heating"], temp)

    async def get_pv_modulation_setpoint_hot_water(self) -> float:
        """Get PV modulation hot water setpoint in °C.

        Register: 303
        German: Solltemperatur TWE PV Modulation
        """
        return await self._read_register(self.registers["pv_modulation_setpoint_hot_water"])

    async def set_pv_modulation_setpoint_hot_water(self, temp: float) -> None:
        """Set PV modulation hot water setpoint in °C.

        Register: 303 (R/W)
        German: Solltemperatur TWE PV Modulation

        Args:
            temp: Temperature setpoint in °C
        """
        await self._write_register(self.registers["pv_modulation_setpoint_hot_water"], temp)
