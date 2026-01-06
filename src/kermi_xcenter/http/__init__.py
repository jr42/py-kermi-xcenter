"""HTTP API client for Kermi x-center.

This module provides an async HTTP client as an alternative to Modbus.
HTTP is more efficient for bulk reads and provides access to additional
datapoints not available via Modbus.

Example:
    ```python
    from kermi_xcenter.http import KermiHttpClient

    async with KermiHttpClient(host="192.168.1.100") as client:
        values = await client.get_all_values(unit_id=40)
        print(values["outdoor_temperature"])

        # List and execute scenes
        scenes = await client.get_scenes()
        await client.execute_scene(scenes[0].scene_id)
    ```
"""

from .client import KermiHttpClient
from .models import (
    Alarm,
    DatapointConfig,
    DeviceInfo,
    HttpDevice,
    Scene,
    SceneOverview,
    SceneState,
)

__all__ = [
    "KermiHttpClient",
    "HttpDevice",
    "DeviceInfo",
    "Alarm",
    "DatapointConfig",
    "Scene",
    "SceneOverview",
    "SceneState",
]
