---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

1. Create client with '...'
2. Call method '...'
3. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

What actually happened.

## Code Example

```python
# Minimal reproducible example
from kermi_modbus import KermiModbusClient, HeatPump

async def reproduce_bug():
    client = KermiModbusClient(host="192.168.1.100")
    heat_pump = HeatPump(client)

    async with client:
        # Your code that triggers the bug
        pass
```

## Environment

- **OS**: [e.g., Ubuntu 22.04, Windows 11, macOS 14]
- **Python Version**: [e.g., 3.12.1]
- **kermi-modbus Version**: [e.g., 0.1.0]
- **pymodbus Version**: [e.g., 3.6.0]
- **Connection Type**: [TCP or RTU]

## Error Messages / Logs

```
Paste any error messages or logs here
```

## Additional Context

Add any other context about the problem here.

## Possible Solution

If you have suggestions on how to fix the bug, please describe them here.
