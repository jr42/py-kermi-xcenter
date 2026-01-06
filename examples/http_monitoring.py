#!/usr/bin/env python3
"""HTTP API monitoring example.

This example demonstrates using the HTTP API client to:
- Discover connected devices
- Read all values efficiently
- Get device metadata
- Read IFM (gateway) data including SmartGrid status
- Check for alarms

Usage:
    python http_monitoring.py --host 192.168.1.100
    python http_monitoring.py --host 192.168.1.100 --password 1234
"""

import argparse
import asyncio

from kermi_xcenter import KermiHttpClient


async def main(host: str, password: str | None = None) -> None:
    """Run HTTP monitoring example."""
    print("=" * 70)
    print(f"Connecting to x-center at {host}")
    print("=" * 70)

    client = KermiHttpClient(host=host, password=password, timeout=30.0)

    async with client:
        # Device discovery happens automatically on connect
        print(f"\nDiscovered {len(client.devices)} device(s):\n")

        for device in client.devices:
            print(f"  {device.display_name}")
            print(f"    Unit ID: {device.unit_id}")
            print(f"    Device Type: {device.device_type}")
            print()

        # Read each device
        for device in client.devices:
            print("=" * 70)
            print(f"{device.display_name} (Unit {device.unit_id})")
            print("=" * 70)

            # Get device info
            try:
                info = await client.get_device_info(device.unit_id)
                print("\nDevice Info:")
                print(f"  Serial Number:    {info.serial_number}")
                print(f"  Model:            {info.model}")
                print(f"  Software Version: {info.software_version}")
            except Exception as e:
                print(f"\nCould not get device info: {e}")

            # Get all values
            try:
                values = await client.get_all_values(device.unit_id)

                if device.unit_id == 0:  # IFM
                    print_ifm_values(values)
                elif device.unit_id == 40:  # Heat Pump
                    print_heat_pump_values(values)
                elif device.unit_id in (50, 51):  # Storage
                    print_storage_values(values, device.unit_id)

            except Exception as e:
                print(f"\nError reading values: {e}")

            print()

        # Check alarms
        print("=" * 70)
        print("Current Alarms")
        print("=" * 70)

        try:
            alarms = await client.get_current_alarms()
            if alarms:
                for alarm in alarms:
                    print(f"  [{alarm.timestamp}] {alarm.message}")
                    print(f"    Device: {alarm.device_id}")
                    print(f"    Acknowledged: {alarm.acknowledged}")
            else:
                print("  No active alarms")
        except Exception as e:
            print(f"  Could not get alarms: {e}")

        print("\n" + "=" * 70)
        print("Done!")
        print("=" * 70)


def print_ifm_values(values: dict) -> None:
    """Print IFM (x-center gateway) values."""
    print("\nSystem:")
    print(f"  Hostname:      {values.get('ifm_hostname', 'N/A')}")
    print(f"  IP Address:    {values.get('ifm_ip_address', 'N/A')}")
    print(f"  Local Time:    {str(values.get('ifm_local_time', 'N/A'))[:19]}")
    print(f"  Alarm Status:  {values.get('ifm_alarm_status', 'N/A')}")

    print("\nNetwork:")
    home_lan = "Connected" if values.get("ifm_home_lan_state") == 1 else "Disconnected"
    internal_lan = "Connected" if values.get("ifm_internal_lan_state") == 1 else "Disconnected"
    remote = "Connected" if values.get("ifm_remote_connected") else "Disconnected"
    print(f"  Home LAN:      {home_lan}")
    print(f"  Internal LAN:  {internal_lan}")
    print(f"  Remote Server: {remote}")

    print("\nSmartGrid / EVU:")
    sg_state = values.get("ifm_smartgrid_state", 0)
    sg_names = {0: "Blocking", 1: "Normal", 2: "Normal", 3: "Boost", 4: "Max Boost"}
    print(f"  EVU Signal:      {'Active' if values.get('ifm_evu_signal') else 'Off'}")
    print(f"  SGReady2 Signal: {'Active' if values.get('ifm_sgready2_signal') else 'Off'}")
    print(f"  SmartGrid State: {sg_state} ({sg_names.get(sg_state, 'Unknown')})")

    print("\nOutputs:")
    print(f"  LED1:    {'On' if values.get('ifm_led1') else 'Off'}")
    print(f"  LED2:    {'On' if values.get('ifm_led2') else 'Off'}")
    print(f"  Output1: {'On' if values.get('ifm_output1') else 'Off'}")
    print(f"  Output2: {'On' if values.get('ifm_output2') else 'Off'}")

    print("\nS0 Energy Meter:")
    print(f"  Power:           {values.get('ifm_s0_power', 0):.1f} W")
    print(f"  Pulses per kWh:  {values.get('ifm_s0_pulses_per_kwh', 'N/A')}")
    print(f"  Sample Interval: {values.get('ifm_s0_sample_interval', 'N/A')} s")


def print_heat_pump_values(values: dict) -> None:
    """Print Heat Pump values."""
    print("\nStatus:")
    status = values.get("heat_pump_status", "N/A")
    print(f"  Heat Pump Status: {status}")
    print(f"  Heating Mode:     {values.get('is_heating_mode', 'N/A')}")
    print(f"  Hot Water Mode:   {values.get('is_hot_water_mode', 'N/A')}")
    print(f"  Cooling Mode:     {values.get('is_cooling_mode', 'N/A')}")
    print(f"  PV Active:        {values.get('pv_modulation_active', 'N/A')}")

    print("\nTemperatures:")
    supply = values.get("supply_temp_heat_pump")
    ret = values.get("return_temp_heat_pump")
    if supply is not None:
        print(f"  Supply:  {supply:.1f} C")
    if ret is not None:
        print(f"  Return:  {ret:.1f} C")

    print("\nPower & Efficiency:")
    power = values.get("power_total")
    elec = values.get("power_electrical_total")
    cop = values.get("cop_total")
    if power is not None:
        print(f"  Thermal Power:    {power:.2f} kW")
    if elec is not None:
        print(f"  Electrical Power: {elec:.2f} kW")
    if cop is not None and cop > 0:
        print(f"  COP:              {cop:.2f}")

    print("\nCompressor:")
    speed = values.get("compressor_speed")
    if speed is not None:
        print(f"  Speed: {speed:.1f} rps")


def print_storage_values(values: dict, unit_id: int) -> None:
    """Print Storage System values."""
    if unit_id == 50:  # Heating storage
        print("\nTemperatures:")
        outdoor = values.get("outdoor_temperature")
        heating = values.get("heating_actual")
        setpoint = values.get("heating_setpoint")
        if outdoor is not None:
            print(f"  Outdoor:  {outdoor:.1f} C")
        if heating is not None:
            print(f"  Heating:  {heating:.1f} C")
        if setpoint is not None:
            print(f"  Setpoint: {setpoint:.1f} C")

        print("\nStatus:")
        print(f"  Summer Mode:  {values.get('summer_mode_active', 'N/A')}")
        print(f"  Cooling Mode: {values.get('cooling_mode_active', 'N/A')}")

    elif unit_id == 51:  # Hot water storage
        print("\nHot Water:")
        actual = values.get("hot_water_actual")
        setpoint = values.get("hot_water_setpoint")
        boost = values.get("hot_water_boost_active")
        if actual is not None:
            print(f"  Temperature: {actual:.1f} C")
        if setpoint is not None:
            print(f"  Setpoint:    {setpoint:.1f} C")
        print(f"  Boost Active: {boost}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP API monitoring example")
    parser.add_argument("--host", required=True, help="x-center hostname or IP")
    parser.add_argument("--password", help="Device password (optional)")

    args = parser.parse_args()
    asyncio.run(main(args.host, args.password))
