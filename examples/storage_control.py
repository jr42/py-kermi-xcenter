"""Storage system control example.

This example demonstrates how to control heating and hot water storage
systems using the StorageSystem device class.
"""

import asyncio

from kermi_modbus import (
    EnergyMode,
    KermiModbusClient,
    SeasonSelection,
    StorageSystem,
)


async def main() -> None:
    """Control storage system settings."""
    client = KermiModbusClient(host="192.168.1.100", port=502)

    # Create storage devices
    heating_storage = StorageSystem(client, unit_id=50)
    hot_water_storage = StorageSystem(client, unit_id=51)

    async with client:
        print("=== Heating Storage (Unit 50) ===\n")

        # Read heating storage values
        heating_actual = await heating_storage.get_heating_actual()
        heating_setpoint = await heating_storage.get_heating_setpoint()
        circuit_actual = await heating_storage.get_heating_circuit_actual()
        circuit_setpoint = await heating_storage.get_heating_circuit_setpoint()
        status = await heating_storage.get_heating_circuit_status()
        energy_mode = await heating_storage.get_heating_circuit_energy_mode()

        print(f"Storage Temperature:      {heating_actual:.1f}°C (setpoint: {heating_setpoint:.1f}°C)")
        print(f"Circuit Temperature:      {circuit_actual:.1f}°C (setpoint: {circuit_setpoint:.1f}°C)")
        print(f"Circuit Status:           {status.name}")
        print(f"Energy Mode:              {energy_mode.name}")

        # Example: Set to ECO mode
        print("\nSetting heating circuit to ECO mode...")
        await heating_storage.set_heating_circuit_energy_mode(EnergyMode.ECO)
        print("✓ Energy mode updated")

        print("\n=== Hot Water Storage (Unit 51) ===\n")

        # Read hot water storage values
        hot_water_actual = await hot_water_storage.get_hot_water_actual()
        hot_water_setpoint = await hot_water_storage.get_hot_water_setpoint()
        hot_water_constant = await hot_water_storage.get_hot_water_setpoint_constant()

        print(f"Hot Water Temperature:    {hot_water_actual:.1f}°C")
        print(f"Current Setpoint:         {hot_water_setpoint:.1f}°C")
        print(f"Constant Setpoint:        {hot_water_constant:.1f}°C")

        # Example: Trigger single charge to 55°C
        print("\nTriggering single charge to 55°C...")
        await hot_water_storage.set_hot_water_single_charge_setpoint(55.0)
        await hot_water_storage.set_hot_water_single_charge_active(True)
        print("✓ Single charge activated")

        # Check activation
        single_charge_active = await hot_water_storage.get_hot_water_single_charge_active()
        print(f"  Single charge active: {single_charge_active}")

        # Example: Set season selection
        print("\nSetting manual season selection to AUTO...")
        await heating_storage.set_season_selection_manual(SeasonSelection.AUTO)
        season = await heating_storage.get_season_selection_manual()
        print(f"✓ Season selection: {season.name}")


if __name__ == "__main__":
    asyncio.run(main())
