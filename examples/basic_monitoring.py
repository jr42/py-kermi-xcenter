"""Basic monitoring example for Kermi heat pump.

This example demonstrates how to read basic values from the heat pump,
including temperatures, COP, power, and status.
"""

import asyncio

from kermi_modbus import HeatPumpStatus, KermiModbusClient, HeatPump


async def main() -> None:
    """Monitor heat pump basic values."""
    # Create client (adjust IP address and port as needed)
    client = KermiModbusClient(host="192.168.1.100", port=502)

    # Create heat pump device (unit ID 40 is default)
    heat_pump = HeatPump(client)

    # Connect and read values
    async with client:
        print("=== Kermi Heat Pump Monitor ===\n")

        # Temperatures
        print("Temperatures:")
        outdoor_temp = await heat_pump.get_outdoor_temperature()
        supply_temp = await heat_pump.get_supply_temp_heat_pump()
        return_temp = await heat_pump.get_return_temp_heat_pump()
        print(f"  Outdoor: {outdoor_temp:.1f}°C")
        print(f"  Supply:  {supply_temp:.1f}°C")
        print(f"  Return:  {return_temp:.1f}°C")

        # Flow rate
        flow_rate = await heat_pump.get_flow_rate_heat_pump()
        print(f"  Flow:    {flow_rate:.1f} l/min")

        # COP values
        print("\nCOP (Coefficient of Performance):")
        cop_total = await heat_pump.get_cop_total()
        cop_heating = await heat_pump.get_cop_heating()
        cop_hot_water = await heat_pump.get_cop_hot_water()
        print(f"  Total:       {cop_total:.2f}")
        print(f"  Heating:     {cop_heating:.2f}")
        print(f"  Hot Water:   {cop_hot_water:.2f}")

        # Power (thermal)
        print("\nThermal Power:")
        power_total = await heat_pump.get_power_total()
        power_heating = await heat_pump.get_power_heating()
        power_hot_water = await heat_pump.get_power_hot_water()
        print(f"  Total:       {power_total:.2f} kW")
        print(f"  Heating:     {power_heating:.2f} kW")
        print(f"  Hot Water:   {power_hot_water:.2f} kW")

        # Power (electrical)
        print("\nElectrical Power:")
        power_el_total = await heat_pump.get_power_electrical_total()
        power_el_heating = await heat_pump.get_power_electrical_heating()
        power_el_hot_water = await heat_pump.get_power_electrical_hot_water()
        print(f"  Total:       {power_el_total:.2f} kW")
        print(f"  Heating:     {power_el_heating:.2f} kW")
        print(f"  Hot Water:   {power_el_hot_water:.2f} kW")

        # Status
        print("\nStatus:")
        status = await heat_pump.get_heat_pump_status()
        alarm = await heat_pump.get_global_alarm()
        print(f"  Mode:   {status.name}")
        print(f"  Alarm:  {'YES' if alarm else 'No'}")

        # Operating hours
        print("\nOperating Hours:")
        hours_fan = await heat_pump.get_operating_hours_fan()
        hours_compressor = await heat_pump.get_operating_hours_compressor()
        print(f"  Fan:        {hours_fan} h")
        print(f"  Compressor: {hours_compressor} h")


if __name__ == "__main__":
    asyncio.run(main())
