"""PV modulation example for Kermi heat pump.

This example demonstrates how to control PV modulation features,
which allow the heat pump to use excess solar power.
"""

import asyncio

from kermi_modbus import KermiModbusClient, HeatPump


async def main() -> None:
    """Control PV modulation settings."""
    client = KermiModbusClient(host="192.168.1.100", port=502)
    heat_pump = HeatPump(client)

    async with client:
        print("=== PV Modulation Control ===\n")

        # Read current status
        pv_active = await heat_pump.get_pv_modulation_status()
        pv_power = await heat_pump.get_pv_modulation_power()
        pv_setpoint_heating = await heat_pump.get_pv_modulation_setpoint_heating()
        pv_setpoint_hot_water = await heat_pump.get_pv_modulation_setpoint_hot_water()

        print("Current PV Modulation Settings:")
        print(f"  Active:              {'Yes' if pv_active else 'No'}")
        print(f"  Power:               {pv_power} W")
        print(f"  Heating Setpoint:    {pv_setpoint_heating:.1f}°C")
        print(f"  Hot Water Setpoint:  {pv_setpoint_hot_water:.1f}°C")

        # Example: Set PV modulation based on available solar power
        available_solar_power = 2500  # Watts from solar system

        if available_solar_power > 500:
            print(f"\nSetting PV modulation to use {available_solar_power}W...")
            await heat_pump.set_pv_modulation_power(available_solar_power)

            # Optionally increase setpoints to use more energy
            await heat_pump.set_pv_modulation_setpoint_heating(23.0)
            await heat_pump.set_pv_modulation_setpoint_hot_water(52.0)

            print("✓ PV modulation configured")

            # Verify settings
            new_power = await heat_pump.get_pv_modulation_power()
            print(f"  Configured power: {new_power}W")
        else:
            print("\nInsufficient solar power for PV modulation")


if __name__ == "__main__":
    asyncio.run(main())
