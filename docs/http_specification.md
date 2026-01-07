# Kermi x-center HTTP API Specification

This document describes the HTTP API provided by the Kermi x-center interface module (IFM). The API is accessed via the device's web interface and provides comprehensive access to all connected devices and their datapoints.

**Tested with:** x-center IFM firmware version 1.6.3.42

## Overview

The HTTP API offers several advantages over Modbus:
- **Efficient bulk reads**: All datapoints for a device in 2 API calls (vs ~30 Modbus calls)
- **Device discovery**: Automatic detection of all connected devices
- **Extended data**: Access to 250+ datapoints (more than Modbus exposes)
- **Metadata**: Device serial numbers, model names, software versions
- **Alarms**: Current and historical alarm access

## Authentication

The API uses session-based authentication with cookies.

### Login

```http
POST /api/Security/Login
Content-Type: application/json

{
  "Password": "1234"
}
```

**Response:**
```json
{
  "isValid": true,
  "changePassword": false,
  "redirectUrl": null
}
```

- Password is typically the last 4 digits of the serial number
- Some devices may allow unauthenticated access
- Session cookie `XCenter` is set on successful login

### Logout

```http
POST /api/Security/Logout
```

## Device Discovery

### Get Favorites (Device List)

The favorites endpoint returns all datapoints configured in the system, from which devices can be extracted.

```http
POST /api/Favorite/GetFavorites/00000000-0000-0000-0000-000000000000
Content-Type: application/json

{
  "WithDetails": true,
  "OnlyHomeScreen": false
}
```

**Response:**
```json
[
  {
    "DeviceId": "6dca4094-8955-49cf-9160-bdc1914ae7f0",
    "DatapointConfig": {
      "DeviceType": 97,
      "DisplayName": "Outdoor temperature",
      "WellKnownName": "LuftTemperatur"
    }
  }
]
```

### Device Types

| DeviceType | Device | Description |
|------------|--------|-------------|
| 0 | IFM | x-center Interface Module (gateway) |
| 95 | StorageSystem | Heating/Hot Water Storage (Puffersystemmodul) |
| 97 | HeatPump | x-change Heat Pump |

### Unit ID Mapping

| Unit ID | Device | Notes |
|---------|--------|-------|
| 0 | IFM | Device ID: 00000000-0000-0000-0000-000000000000 |
| 40 | Heat Pump | Main heat pump unit |
| 50 | Heating Storage | First StorageSystem device |
| 51 | Hot Water Storage | Second StorageSystem device |

## Reading Datapoints

### Get All Datapoints for a Device

```http
POST /api/Menu/GetBundlesByCategory
Content-Type: application/json

{
  "DeviceId": "6dca4094-8955-49cf-9160-bdc1914ae7f0",
  "Category": 0
}
```

**Categories:**
- `0`: Read-only sensor values and status
- `1`: Writable settings and controls

**Response:**
```json
[
  {
    "DatapointBundleId": "bundle-uuid",
    "Datapoints": [
      {
        "Config": {
          "DatapointConfigId": "config-uuid",
          "DisplayName": "Outdoor temperature",
          "WellKnownName": "LuftTemperatur",
          "Unit": "°C",
          "Category": 0,
          "DeviceType": 95
        },
        "DatapointValue": {
          "Value": -0.9,
          "DeviceId": "device-uuid",
          "Flags": 0
        }
      }
    ]
  }
]
```

## Writing Datapoints

### Write Values

```http
POST /api/Datapoint/WriteValues
Content-Type: application/json

{
  "DatapointValues": [
    {
      "DatapointConfigId": "config-uuid",
      "DeviceId": "device-uuid",
      "Value": 50.0
    }
  ]
}
```

**Important:** Only Category 1 datapoints are writable. The library restricts writes to safe, user-facing settings only.

## Alarms

### Get Current Alarms

```http
POST /api/Alarm/GetCurrentAlarms
Content-Type: application/json
{}
```

### Get Alarm History

```http
POST /api/Alarm/GetAlarmHistory
Content-Type: application/json
{}
```

### Clear Current Alarms

```http
POST /api/Alarm/ClearCurrentAlarms
Content-Type: application/json
{}
```

## Menu Navigation

### Get Child Menu Entries

```http
POST /api/Menu/GetChildEntries
Content-Type: application/json

{
  "DeviceId": "00000000-0000-0000-0000-000000000000",
  "ParentMenuEntryId": "00000000-0000-0000-0000-000000000000",
  "WithDetails": true
}
```

## Scenes (Automation)

Scenes are automation rules that execute actions when conditions are met. The API provides endpoints to list, read, and execute scenes.

### Get All Scenes

Use `GetScenesByDeviceId` with the IFM device ID to list all scenes:

```http
POST /api/Scene/GetScenesByDeviceId
Content-Type: application/json

{
  "DeviceId": "00000000-0000-0000-0000-000000000000"
}
```

**Response:**
```json
[
  {
    "SceneId": "f29e1596-5efb-4b5e-8674-5baf2b65a377",
    "DisplayName": "PV Modulation",
    "Description": null,
    "Priority": 100,
    "Enabled": true,
    "LastUpdate": "2024-01-15T10:30:00Z",
    "State": {
      "ConditionIsTrue": false,
      "ActionIsRunning": false,
      "LastCheck": "2024-01-15T12:00:00Z",
      "ExecutionTimeMs": 15
    }
  }
]
```

**Note:** `GetAllScenes` returns 405 on local devices (cloud-only). Use `GetScenesByDeviceId` with IFM device ID as workaround.

### Get Scene Details

```http
POST /api/Scene/GetSceneById
Content-Type: application/json

{
  "SceneId": "f29e1596-5efb-4b5e-8674-5baf2b65a377"
}
```

Returns full scene with conditions and actions:

```json
{
  "SceneId": "f29e1596-5efb-4b5e-8674-5baf2b65a377",
  "DisplayName": "PV Modulation",
  "Priority": 100,
  "Enabled": true,
  "ConditionTreeData": {
    "NodeType": 0,
    "Children": [...]
  },
  "ActionData": [
    {
      "ActionType": 0,
      "DatapointConfigId": "...",
      "Value": 1000
    }
  ]
}
```

### Get Scene State

```http
POST /api/Scene/GetSceneOverviewById
Content-Type: application/json

{
  "SceneId": "f29e1596-5efb-4b5e-8674-5baf2b65a377"
}
```

Returns scene metadata with current execution state (whether conditions are met, whether actions are running).

### Execute Scene

Triggers a scene's actions immediately, regardless of conditions:

```http
POST /api/Scene/ExecuteScene
Content-Type: application/json

{
  "SceneId": "f29e1596-5efb-4b5e-8674-5baf2b65a377"
}
```

### Create/Update/Delete Scenes

The following endpoints exist but are **not implemented in this library** (read + execute only):

- `POST /api/Scene/AddOrUpdateScene` - Create or update a scene
- `POST /api/Scene/RemoveScene` - Delete a scene

## Key Datapoint Mappings

### IFM (Unit 0)

| WellKnownName | Description | Category |
|---------------|-------------|----------|
| `SoftwareVersion` | IFM software version | 0 |
| `SystemSerialNo` | Serial number | 1 |
| `DH_SGReady1` | EVU signal input | 0 |
| `DH_SGReady2` | SGReady2 signal input | 0 |
| `DH_SmartGridState` | SmartGrid state (0-4) | 0 |
| `DH_Led1`, `DH_Led2` | LED outputs | 1 |
| `DH_Output1`, `DH_Output2` | Digital outputs | 1 |
| `S0_1_W` | S0 energy meter power | 0 |
| `HomeIPAddress` | Network IP address | 1 |

### Heat Pump (Unit 40)

| WellKnownName | Description | Category |
|---------------|-------------|----------|
| `Rubin_CombinedHeatpumpState` | Heat pump status | 0 |
| `Rubin_CurrentCOP` | Current COP | 0 |
| `Rubin_CurrentOutputCapacity` | Thermal power output | 0 |
| `Rubin_CurrentPowerInverter` | Electrical power consumption | 0 |
| `LuftTemperatur` | Outdoor temperature | 0 |
| `Rubin_SecondaryOutletTemp` | Supply temperature | 0 |
| `Rubin_PvModulationPower` | PV modulation setpoint | 1 |

### Storage System (Units 50/51)

| WellKnownName | Description | Category |
|---------------|-------------|----------|
| `BufferSystem_HeatingTemperatureActual` | Heating buffer temperature | 0 |
| `BufferSystem_TweTemperatureActual` | Hot water temperature | 0 |
| `BufferSystem_OneTimeTwe` | One-time hot water boost | 1 |
| `BufferSystem_TemperatureSetpointTwe` | Hot water setpoint | 1 |
| `HeatingCircuit_EnergyMode` | Energy mode setting | 1 |
| `HeatingCircuit_OperationType` | Operating type setting | 1 |

## SmartGrid States

| Value | State | Description |
|-------|-------|-------------|
| 0 | Blocking | EVU blocking active |
| 1 | Normal | Standard operation |
| 2 | Normal | Standard operation (variant) |
| 3 | Boost | Increased heating allowed |
| 4 | Max Boost | Maximum heating power |

## Response Format

All API responses follow this format:

```json
{
  "ResponseData": { ... },
  "StatusCode": 0,
  "ExceptionData": null,
  "DisplayText": "",
  "DetailedText": ""
}
```

- `StatusCode`: 0 = success, non-zero = error
- `ResponseData`: Contains the actual response data
- `DisplayText` / `DetailedText`: Error messages when `StatusCode` is non-zero

## Session Handling

- Sessions expire after inactivity (typically 30 minutes)
- Expired sessions return HTML instead of JSON
- Re-authentication is required when session expires
- The library handles automatic re-authentication

## Extending the API

To add support for additional datapoints:

1. **Find the WellKnownName**: Query `GetBundlesByCategory` for the device
2. **Add mapping**: Add to `WELLKNOWN_TO_ATTR` in `http/mapping.py`
3. **Mark writable**: If Category 1, add to `WRITABLE_DATAPOINTS` (if safe to write)
4. **Add restrictions**: If dangerous, add to `RESTRICTED_DATAPOINTS`

### Example: Adding a new datapoint

```python
# In http/mapping.py

WELLKNOWN_TO_ATTR = {
    ...
    "NewDatapoint_WellKnownName": "new_datapoint_name",
}

# If writable (Category 1) and safe for users:
WRITABLE_DATAPOINTS = {
    ...
    "new_datapoint_name",
}
```

## Notes

- The IFM device (unit 0) is always available at device ID `00000000-0000-0000-0000-000000000000`
- Some datapoints have no `WellKnownName` - these use `DisplayName` as fallback
- Heat Pump device info (serial, model) uses `DisplayName` mapping
- Storage devices only have "Buffer System" as their model name via API
