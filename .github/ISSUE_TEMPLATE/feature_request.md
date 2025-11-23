---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

A clear and concise description of the feature you'd like to see.

## Problem Statement

Is your feature request related to a problem? Please describe.
Example: "I'm always frustrated when [...]"

## Proposed Solution

Describe the solution you'd like to see implemented.

## Example Usage

```python
# Show how you'd like to use this feature
from kermi_modbus import KermiModbusClient, HeatPump

async def example():
    client = KermiModbusClient(host="192.168.1.100")
    heat_pump = HeatPump(client)

    async with client:
        # Your proposed API usage
        result = await heat_pump.new_feature()
```

## Alternatives Considered

Describe any alternative solutions or features you've considered.

## Additional Context

Add any other context, screenshots, or examples about the feature request here.

## Impact

- [ ] This would be a breaking change
- [ ] This requires new dependencies
- [ ] This affects all device types (HeatPump, StorageSystem, UniversalModule)
- [ ] This is specific to one device type

## Implementation Ideas

If you have ideas on how to implement this, please share them here.
