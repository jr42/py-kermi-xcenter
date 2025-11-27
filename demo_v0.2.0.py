#!/usr/bin/env python3
"""Demonstration of v0.2.0 features: automatic None handling and discovery."""

import asyncio
import logging

from kermi_xcenter import HeatPump, KermiModbusClient, StorageSystem, UniversalModule
from kermi_xcenter.utils.discovery import save_capabilities, load_capabilities

# Enable debug logging to see the new behavior
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Replace with your heat pump IP
    client = KermiModbusClient(host="192.168.178.55", port=502, timeout=2)

    async with client:
        print("\n" + "="*70)
        print("v0.2.0 Feature Demo: Pythonic None Handling")
        print("="*70)

        # ================================================================
        # Feature 1: Individual getters now return None for unavailable
        # ================================================================
        print("\n1. Individual getters return None (no exceptions):")
        print("-" * 70)

        hp = HeatPump(client)

        # This will work (available register)
        outdoor_temp = await hp.get_outdoor_temperature()
        print(f"   Outdoor temperature: {outdoor_temp}°C")

        # This might return None if not available (no exception!)
        flow_rate = await hp.get_flow_rate_heat_pump()
        if flow_rate is not None:
            print(f"   Flow rate: {flow_rate} l/min")
        else:
            print(f"   Flow rate: Not available on this device")

        # ================================================================
        # Feature 2: Device capability discovery
        # ================================================================
        print("\n2. Discover which registers are available:")
        print("-" * 70)

        print("\n   Discovering HeatPump capabilities...")
        hp_caps = await hp.discover_capabilities()
        available = sum(1 for v in hp_caps.values() if v)
        print(f"   Found {available}/{len(hp_caps)} available registers")

        # Save capabilities for reuse
        save_capabilities(hp_caps, "heat_pump_capabilities.json")
        print(f"   Saved to heat_pump_capabilities.json")

        # ================================================================
        # Feature 3: Use pre-discovered capabilities for faster operation
        # ================================================================
        print("\n3. Reuse capabilities (skips unavailable registers):")
        print("-" * 70)

        # Load saved capabilities
        caps = load_capabilities("heat_pump_capabilities.json")

        # Create new instance with capabilities - unavailable registers are skipped!
        hp_fast = HeatPump(client, capabilities=caps)

        print("   Reading all values with cached capabilities...")
        values = await hp_fast.get_all_readable_values()
        none_count = sum(1 for v in values.values() if v is None)
        print(f"   Retrieved {len(values) - none_count}/{len(values)} values")
        print(f"   (Skipped {none_count} unavailable registers - much faster!)")

        # ================================================================
        # Feature 4: Check other units
        # ================================================================
        print("\n4. Check other device units:")
        print("-" * 70)

        # Storage System (Unit 50)
        storage = StorageSystem(client, unit_id=50)
        storage_caps = await storage.discover_capabilities()
        available_storage = sum(1 for v in storage_caps.values() if v)
        print(f"   Storage System (Unit 50): {available_storage}/{len(storage_caps)} registers available")

        # Universal Module (Unit 30)
        universal = UniversalModule(client, unit_id=30)
        universal_caps = await universal.discover_capabilities()
        available_universal = sum(1 for v in universal_caps.values() if v)
        print(f"   Universal Module (Unit 30): {available_universal}/{len(universal_caps)} registers available")

        print("\n" + "="*70)
        print("Demo complete! Key improvements in v0.2.0:")
        print("  ✓ No more exceptions for unavailable registers (returns None)")
        print("  ✓ Automatic connection recovery (transparent)")
        print("  ✓ Device capability discovery")
        print("  ✓ Capability caching for faster operation")
        print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
