"""Mapping between HTTP API WellKnownNames and Python attribute names.

This module provides mappings for all 250+ HTTP API datapoints to Python-friendly
attribute names. It also defines which datapoints are writable.
"""

# WellKnownName → Python attribute name
# This maps the HTTP API's WellKnownName field to library attribute names
WELLKNOWN_TO_ATTR: dict[str, str] = {
    # =========================================================================
    # HEAT PUMP (Unit 40) - Device Type 97
    # =========================================================================
    # Status
    "Rubin_CombinedHeatpumpState": "heat_pump_status",
    "Rubin_StateSinceUtc": "status_since",
    "Rubin_IsTweState": "is_hot_water_mode",
    "Rubin_IsHeatingState": "is_heating_mode",
    "Rubin_IsCoolingState": "is_cooling_mode",
    "Rubin_IsDefrostingState": "is_defrosting",
    "Rubin_PvIsActive": "pv_modulation_active",
    "Rubin_PvEnabled": "pv_modulation_enabled",
    "Rubin_PvAvailablePower": "pv_available_power",
    "Rubin_PvSetpointPower": "pv_setpoint_power",
    "Rubin_PvTurnOnPower": "pv_turn_on_power",
    "Rubin_PvTurnOffPower": "pv_turn_off_power",
    "Rubin_PvPreDelay": "pv_pre_delay",
    "Rubin_PvPostDelay": "pv_post_delay",
    "Rubin_PvTemperatureSetpointPVTwe": "pv_setpoint_temp_hot_water",
    "Rubin_PvTemperatureSetpointPVHeating": "pv_setpoint_temp_heating",
    "Rubin_PvTemperatureSetpointPVCooling": "pv_setpoint_temp_cooling",
    "Rubin_PvEnsureSetpointsAfterMinutes": "pv_ensure_setpoints_delay",
    "Rubin_CurrentPowerInverterPV": "pv_electrical_power",
    "Rubin_CurrentPowerInverterHeatingPV": "pv_electrical_power_heating",
    "Rubin_CurrentPowerInverterTwePV": "pv_electrical_power_hot_water",
    "Rubin_CurrentPowerInverterCoolingPV": "pv_electrical_power_cooling",
    # Temperatures - Energy Source
    "Rubin_Link_B14_EnergiequellenAustrittstemperatur": "energy_source_outlet",
    "Rubin_Link_B15_EnergiequellenEintrittstemperatur": "energy_source_inlet",
    # Temperatures - Heat Pump Circuit
    "Rubin_SecondaryOutletTemp": "supply_temp_heat_pump",
    "Rubin_SecondaryInletTemp": "return_temp_heat_pump",
    # Temperatures - Refrigerant Circuit
    "Rubin_Link_B11_Saugtemperatur": "suction_temperature",
    "Rubin_Link_B12_Heissgastemperatur": "hot_gas_temperature",
    "Rubin_Link_B20_Unterkuehlungstemperatur": "subcooling_temperature",
    "Rubin_Link_B22_TemperaturNachVerdampfer": "temperature_after_evaporator",
    "Rubin_Link_B23_Verdampferoberflaechentemperatur": "evaporator_surface_temperature",
    "Rubin_Link_Kondensationstemperatur": "condensation_temperature",
    "Rubin_Link_Verdampfungstemperatur": "evaporation_temperature",
    # Power & Efficiency - Total
    "Rubin_CurrentOutputCapacity": "power_total",
    "Rubin_CurrentPowerInverter": "power_electrical_total",
    "Rubin_CurrentCOP": "cop_total",
    # Power & Efficiency - Hot Water (TWE)
    "Rubin_CurrentOutputCapacityTwe": "power_hot_water",
    "Rubin_CurrentPowerInverterTwe": "power_electrical_hot_water",
    "Rubin_CurrentCOPTwe": "cop_hot_water",
    # Power & Efficiency - Heating
    "Rubin_CurrentOutputCapacityHeating": "power_heating",
    "Rubin_CurrentPowerInverterHeating": "power_electrical_heating",
    "Rubin_CurrentCOPHeating": "cop_heating",
    # Power - Cooling
    "Rubin_CurrentOutputCapacityCooling": "power_cooling",
    "Rubin_CurrentPowerInverterCooling": "power_electrical_cooling",
    "Rubin_CurrentCOPCooling": "cop_cooling",
    # Power Limits
    "Rubin_MinPowerKW": "min_heating_power",
    "Rubin_MaxPowerKW": "max_heating_power",
    "Rubin_PvCalculatedOutputHeatingPowerInKW": "pv_calculated_heating_power",
    # Pressures
    "Rubin_Link_P11_Niederdruck": "low_pressure",
    "Rubin_Link_P12_Hochdruck": "high_pressure",
    "Rubin_PulpActualValue": "flow_rate_heat_pump",
    # Compressor
    "Rubin_Link_Verdichterzahl": "compressor_speed",
    # Superheat / Subcooling
    "Rubin_Link_SshAktuell": "ssh_current",
    "Rubin_Link_DshAktuell": "dsh_current",
    "Rubin_Link_SollwertSsh": "ssh_setpoint",
    "Rubin_Link_SollwertDsh": "dsh_setpoint",
    # EEV (Electronic Expansion Valve)
    "Rubin_AktuelleOeffnung": "eev_opening",
    # Valves & Pumps
    "Rubin_3WayValve": "three_way_valve_position",
    "Rubin_CoolingValve": "cooling_valve_position",
    "Rubin_StorageChargingPumpState": "storage_charging_pump_state",
    # Software Info
    "Rubin_SWVersion_Major": "software_version_major",
    "Rubin_SWVersion_Minor": "software_version_minor",
    "Rubin_SWVersion_Patch": "software_version_patch",
    "Rubin_DeviceSubType": "device_subtype",
    # PV Modulation
    "Rubin_PvModulationPower": "pv_modulation_power",
    # =========================================================================
    # STORAGE SYSTEM (Units 50, 51) - Device Type 95
    # =========================================================================
    # Device Info
    "DeviceType": "device_type_name",
    "Serialnumber": "serial_number",
    "BufferSystem_BootloaderVersion": "bootloader_version",
    "PowerModule_SWVersion_Major": "power_module_sw_major",
    "PowerModule_SWVersion_Minor": "power_module_sw_minor",
    "PowerModule_SWVersion_Patch": "power_module_sw_patch",
    # Status
    "HeatingCircuit_SummerMode": "summer_mode_active",
    "HeatingCircuit_ChangeOver": "cooling_mode_active",
    "HeatingCircuit_DetailStatus": "heating_circuit_detail_status",
    "BufferSystem_HeaterIsPVActive": "pv_heating_active",
    # Bivalence Status
    "BufferSystem_BivalenceStateDetailHeating": "external_heat_gen_status_heating",
    "BufferSystem_BivalenceStateDetailTwe": "external_heat_gen_status_hot_water",
    # Pump/Output Status
    "BufferSystem_StateUni1": "output_1_state",
    "BufferSystem_StateUni2": "output_2_state",
    # Temperatures - Heating Storage
    "BufferSystem_HeatingTemperatureActual": "heating_actual",
    "BufferSystem_HeatingSetpoint": "heating_setpoint",
    # Temperatures - Cooling Storage
    "BufferSystem_CoolingTemperatureActual": "cooling_actual",
    "BufferSystem_CoolingSetpoint": "cooling_setpoint",
    # Temperatures - Hot Water (TWE)
    "BufferSystem_TweTemperatureActual": "hot_water_actual",
    "BufferSystem_TweSetpoint": "hot_water_setpoint",
    # Temperatures - Heating Circuit
    "HeatingCircuit_TemperatureActualValue": "heating_circuit_actual",
    # Outdoor Temperature
    "LuftTemperatur": "outdoor_temperature",
    "Aussentemperatur_gemittelt": "outdoor_temperature_avg",
    "HP_Aussentemperatur_Saison": "outdoor_temperature_season",
    # Temperature Sensors
    "BufferSystem_Tsensor1": "t1_temperature",
    "BufferSystem_Tsensor2": "t2_temperature",
    "BufferSystem_Tsensor3": "t3_temperature",
    "BufferSystem_Tsensor4": "t4_temperature",
    # Heating Circuit Control
    "HeatingCircuit_MixerPosition": "mixer_position",
    "HeatingCircuit_OperatingHoursPump": "operating_hours_circuit_pump",
    # Hot Water One-Time Boost (Category 1 - writable)
    "BufferSystem_OneTimeTwe": "hot_water_boost_active",
    "BufferSystem_OneTimeTweSetpoint": "hot_water_boost_setpoint",
    # Hot Water Settings (Category 1 - writable)
    "BufferSystem_TweEnableUser": "hot_water_enabled",
    "BufferSystem_TemperatureSetpointTwe": "hot_water_setpoint_constant",
    "BufferSystem_HeaterTemperatureSetpointPVTwe": "hot_water_setpoint_pv",
    "BufferSystem_TemperatureMinTwe": "hot_water_temp_min",
    "BufferSystem_TemperatureMaxTwe": "hot_water_temp_max",
    "BufferSystem_ErrorSetpointTwe": "hot_water_error_setpoint",
    "BufferSystem_OffsetTwe": "hot_water_overheating_offset",
    # Bivalence Settings (Category 1 - writable)
    "BufferSystem_BivalenceControlTwe": "external_heat_gen_mode_hot_water",
    "BufferSystem_BivalenceModeTwe": "bivalence_mode_hot_water",
    "BufferSystem_AussentempParallelTwe": "bivalence_parallel_temp_hot_water",
    "BufferSystem_AktivBeiStoerungTwe": "external_heat_gen_on_error_hot_water",
    "BufferSystem_AktivBeiEVUSperreTwe": "external_heat_gen_on_evu_lock_hot_water",
    # Heating Circuit Settings
    "BufferSystem_BivalenceControlHeating": "external_heat_gen_mode_heating",
    "HeatingCircuit_OperationType": "heating_circuit_operating_type",
    "HeatingCircuit_EnergyMode": "heating_circuit_energy_mode",
    "HeatingCircuit_ParallelOffset": "heating_curve_parallel_offset",
    "HeatingCircuit_SeasonModeManual": "season_selection_manual",
    "HeatingCircuit_SummerModeTemperature": "summer_mode_heating_off",
    "HeatingCircuit_WinterModeTemperature": "winter_mode_heating_on",
    "HeatingCircuit_CoolingOnTemperature": "cooling_mode_on",
    "HeatingCircuit_CoolingOffTemperature": "cooling_mode_off",
    # =========================================================================
    # IFM - x-center Interface Module (Unit 0) - Device Type 0
    # The x-center gateway device itself
    # =========================================================================
    # System Info (Category 0 - read-only)
    "SoftwareVersion": "ifm_software_version",
    "OSVersion": "ifm_os_version",
    "SystemSerialNo": "ifm_serial_number",
    "HardwareKey": "ifm_hardware_key",
    "LocalTime": "ifm_local_time",
    "GlobalAlarmFlag": "ifm_alarm_status",
    "System_DisplayVersion": "ifm_display_version",
    "System_DisplayLastConnectionTime": "ifm_display_last_connection",
    # Network Status (Category 0 - read-only)
    "HomeNetOperationState": "ifm_home_lan_state",
    "InternalNetOperationState": "ifm_internal_lan_state",
    "RemoteControlConnected": "ifm_remote_connected",
    # SmartGrid / EVU Inputs (Category 0 - read-only)
    "DH_SGReady1": "ifm_evu_signal",
    "DH_SGReady2": "ifm_sgready2_signal",
    "DH_SmartGridState": "ifm_smartgrid_state",
    # S0 Energy Meter (Category 0 - read-only)
    "S0_1_W": "ifm_s0_power",
    "S0_1_Interval": "ifm_s0_interval",
    # Memory Info (Category 0 - read-only)
    "System_MemoryFreeFlash": "ifm_memory_free_flash",
    "System_MemoryFreeSDCard": "ifm_memory_free_sdcard",
    # Time Components (Category 0 - read-only)
    "YearLocal": "ifm_year",
    "MonthLocal": "ifm_month",
    "DayLocal": "ifm_day",
    "DayOfWeekLocal": "ifm_day_of_week",
    "HourLocal": "ifm_hour",
    "MinuteLocal": "ifm_minute",
    # LED & Output Control (Category 1 - writable)
    "DH_Led1": "ifm_led1",
    "DH_Led2": "ifm_led2",
    "DH_Output1": "ifm_output1",
    "DH_Output2": "ifm_output2",
    "DH_SendErrorToOutputs": "ifm_error_output_enabled",
    # S0 Energy Meter Settings (Category 1 - writable)
    "S0_1_RatePerKwh": "ifm_s0_pulses_per_kwh",
    "S0_1_SampleInterval": "ifm_s0_sample_interval",
    # Network Settings (Category 1)
    "SystemHostName": "ifm_hostname",
    "HomeIPAddress": "ifm_ip_address",
    "HomeNetmask": "ifm_netmask",
    "HomeGateway": "ifm_gateway",
    "HomeDNSServer": "ifm_dns_server",
    "HomeEnableDhcp": "ifm_dhcp_enabled",
    # Remote Access (Category 1)
    "RemoteControlEnabled": "ifm_remote_enabled",
    # System Control (Category 1 - dangerous, restricted)
    "SystemRestartOS": "ifm_restart",
    "SystemFactoryReset": "ifm_factory_reset",
}

# Reverse mapping: Python attribute name → WellKnownName
ATTR_TO_WELLKNOWN: dict[str, str] = {v: k for k, v in WELLKNOWN_TO_ATTR.items()}


# Device type to default unit ID mapping
# Note: StorageSystem (95) can be unit 50 (heating) or 51 (hot water)
DEVICE_TYPE_TO_UNIT: dict[int, int] = {
    0: 0,  # IFM (x-center gateway)
    97: 40,  # HeatPump
    95: 50,  # StorageSystem (default to heating, 51 for hot water)
}


# Writable datapoints (user-facing settings only)
# These are safe to write via the HTTP API
WRITABLE_DATAPOINTS: set[str] = {
    # Hot water boost control
    "hot_water_boost_active",
    "hot_water_boost_setpoint",
    # Hot water settings
    "hot_water_enabled",
    "hot_water_setpoint_constant",
    "hot_water_setpoint_pv",
    # Heating circuit settings
    "heating_circuit_operating_type",
    "heating_circuit_energy_mode",
    "heating_curve_parallel_offset",
    # Season/mode control
    "season_selection_manual",
    "summer_mode_heating_off",
    "winter_mode_heating_on",
    "cooling_mode_on",
    "cooling_mode_off",
    # External heat generator mode
    "external_heat_gen_mode_heating",
    "external_heat_gen_mode_hot_water",
    # PV modulation
    "pv_modulation_power",
    "pv_modulation_enabled",
    "pv_available_power",
    "pv_setpoint_power",
    "pv_turn_on_power",
    "pv_turn_off_power",
    "pv_pre_delay",
    "pv_post_delay",
    "pv_setpoint_temp_hot_water",
    "pv_setpoint_temp_heating",
    "pv_setpoint_temp_cooling",
    "pv_ensure_setpoints_delay",
    # IFM - LED & Output Control
    "ifm_led1",
    "ifm_led2",
    "ifm_output1",
    "ifm_output2",
    "ifm_error_output_enabled",
    # IFM - S0 Energy Meter Settings
    "ifm_s0_pulses_per_kwh",
    "ifm_s0_sample_interval",
}


# DisplayName → Python attribute name
# Fallback mapping for datapoints without WellKnownNames (e.g., Heat Pump device info)
DISPLAYNAME_TO_ATTR: dict[str, str] = {
    # Heat Pump device info (no WellKnownName)
    "Serial number": "serial_number",
    "Seriennummer": "serial_number",
    "Production number": "production_number",
    "Produktionsnummer": "production_number",
    "Device name": "device_name",
    "Gerätename": "device_name",
    "Name heat pump": "heat_pump_model",
    "Bezeichnung Wärmepumpe": "heat_pump_model",
    "Device subtype": "device_subtype_name",
    "Geräte Subtyp": "device_subtype_name",
}


# Datapoints that should NOT be exposed for writing (dangerous/non-user-facing)
# These exist in Category 1 but are restricted from the library API
# Includes: calibration values, pressure setpoints, service parameters, etc.
RESTRICTED_DATAPOINTS: set[str] = {
    # Pressure and refrigerant circuit parameters (service only)
    "ssh_setpoint",
    "dsh_setpoint",
    # Temperature limits (could cause damage if set incorrectly)
    "hot_water_temp_min",
    "hot_water_temp_max",
    # Error handling (should not be user-modified)
    "hot_water_error_setpoint",
    "hot_water_overheating_offset",
    # Bivalence advanced parameters
    "bivalence_mode_hot_water",
    "bivalence_parallel_temp_hot_water",
    "external_heat_gen_on_error_hot_water",
    "external_heat_gen_on_evu_lock_hot_water",
    # IFM - Dangerous system controls
    "ifm_restart",
    "ifm_factory_reset",
    # IFM - Network settings (could disconnect device)
    "ifm_hostname",
    "ifm_ip_address",
    "ifm_netmask",
    "ifm_gateway",
    "ifm_dns_server",
    "ifm_dhcp_enabled",
    "ifm_remote_enabled",
}
