"""Continuous monitoring example with periodic updates.

This example demonstrates continuous monitoring of key heat pump values
with periodic updates every 30 seconds.
"""

import asyncio
from datetime import datetime

from kermi_modbus import HeatPump, KermiModbusClient


async def monitor_heat_pump(heat_pump: HeatPump, interval: int = 30) -> None:
    """Continuously monitor heat pump values.

    Args:
        heat_pump: HeatPump device instance
        interval: Update interval in seconds
    """
    print("Starting continuous monitoring (Ctrl+C to stop)...\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Read key values
            outdoor_temp = await heat_pump.get_outdoor_temperature()
            supply_temp = await heat_pump.get_supply_temp_heat_pump()
            cop_total = await heat_pump.get_cop_total()
            power_total = await heat_pump.get_power_total()
            power_electrical = await heat_pump.get_power_electrical_total()
            status = await heat_pump.get_heat_pump_status()

            # Display update
            print(f"[{timestamp}]")
            print(f"  T_outdoor: {outdoor_temp:6.1f}°C  |  T_supply: {supply_temp:6.1f}°C")
            print(f"  COP:       {cop_total:6.2f}    |  Status: {status.name}")
            print(f"  P_thermal: {power_total:6.2f} kW |  P_electrical: {power_electrical:6.2f} kW")
            print()

            # Wait for next update
            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


async def main() -> None:
    """Main function."""
    client = KermiModbusClient(host="192.168.1.100", port=502)
    heat_pump = HeatPump(client)

    async with client:
        await monitor_heat_pump(heat_pump, interval=30)


if __name__ == "__main__":
    asyncio.run(main())
