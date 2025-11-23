# Kermi Heat Pump Modbus Specification

## Supported Modbus Functions

- `0x03` - Read Holding Registers
- `0x06` - Write Single Register
- `0x10` - Write Multiple Registers

## Modbus Modules

### 1. Wärmepumpe (Heat Pump)
**Unit ID:** 40

#### Register Map

| Address | Attribute | Unit | Code | Name | Description |
|---------|-----------|------|------|------|-------------|
| 1 | R | °C | B14 | energiequelle_austritt | Energiequelle Austrittstemperatur |
| 2 | R | °C | B15 | energiequelle_eintritt | Energiequelle Eintrittstemperatur |
| 3 | R | °C | BOT | aussentemperatur | Außentemperaturfühler |
| 50 | R | °C | B16 | vorlauf_wp | Vorlauftemperatur Wärmepumpe |
| 51 | R | °C | B17 | ruecklauf_wp | Rücklauftemperatur Wärmepumpe |
| 52 | R | l/min | P13 | durchfluss_wp | Durchfluss Wärmepumpe |
| 100 | R | - | - | cop_aktuell | Aktueller COP gesamt |
| 101 | R | - | - | cop_heizen | Aktueller COP Heizen |
| 102 | R | - | - | cop_twe | Aktueller COP Trinkwassererwärmung |
| 103 | R | - | - | cop_kuehlen | Aktueller COP Kühlen |
| 104 | R | kW | - | leistung_aktuell | Aktuelle Leistung gesamt |
| 105 | R | kW | - | leistung_heizen | Aktuelle Leistung Heizen |
| 106 | R | kW | - | leistung_twe | Aktuelle Leistung TWE |
| 107 | R | kW | - | leistung_kuehlen | Aktuelle Leistung Kühlen |
| 108 | R | kW | - | leistung_el_aktuell | Aktuelle elektrische Leistung gesamt |
| 109 | R | kW | - | leistung_el_heizen | Aktuelle elektrische Leistung Heizen |
| 110 | R | kW | - | leistung_el_twe | Aktuelle elektrische Leistung TWE |
| 111 | R | kW | - | leistung_el_kuehlen | Aktuelle elektrische Leistung Kühlen |
| 150 | R | h | - | bh_luefter | Betriebsstunden Lüfter |
| 151 | R | h | - | bh_speicherladepumpe | Betriebsstunden Speicherladepumpe |
| 152 | R | h | - | bh_verdichter | Betriebsstunden Verdichter |

#### Status Wärmepumpe (Address 200)
- Attribute: R
- Enum Values:
  - 0: Standby
  - 1: Alarm
  - 2: TWE
  - 3: Kühlen
  - 4: Heizen
  - 5: Abtauung
  - 6: Vorbereitung
  - 7: Blockiert
  - 8: EVU Sperre
  - 9: nicht verfügbar

#### Globaler Alarm (Address 250)
- Attribute: R
- Enum Values:
  - 0: Nein
  - 1: Ja

#### PV Modulation

| Address | Attribute | Unit | Name | Description |
|---------|-----------|------|------|-------------|
| 300 | R | - | pv_modulation_status | Status PV Modulation Wärmepumpe (0=Nein, 1=Ja) |
| 301 | R/W | W | pv_modulation_leistung | Aktuelle Leistung PV Modulation |
| 302 | R/W | °C | pv_modulation_soll_hz | Solltemperatur Heizkreis PV Modulation |
| 303 | R/W | °C | pv_modulation_soll_twe | Solltemperatur TWE PV Modulation |

---

### 2. Speichersystemmodul (Storage System Module)

**Unit ID:**
- 50 for heating storage
- 51 for TWE (hot water) storage

**Note:** Same register map applies to both unit IDs.

#### Register Map

| Address | Attribute | Unit | Min | Max | Default | Name | Description |
|---------|-----------|------|-----|-----|---------|------|-------------|
| 1 | R | °C | - | - | - | heizen_ist | Isttemperatur Heizspeicher |
| 2 | R | °C | - | - | - | heizen_soll | Solltemperatur Heizspeicher |
| 50 | R | °C | - | - | - | kuehlen_ist | Isttemperatur Kühlspeicher |
| 51 | R | °C | - | - | - | kuehlen_soll | Solltemperatur Kühlspeicher |
| 100 | R | °C | - | - | - | twe_ist | Isttemperatur TWE |
| 101 | R | °C | - | - | - | twe_soll | Solltemperatur TWE |
| 102 | R/W | °C | 0 | 85 | 48 | twe_soll_konstant | Konstanter Sollwert TWE |
| 103 | R/W | - | 0 | 1 | 0 | twe_einmalladung_aktiv | Einmalladung TWE (0=Aus, 1=Ein) |
| 104 | R/W | °C | 30 | 60 | 50 | twe_einmalladung_soll | Sollwert Einmalladung TWE |

#### Heizkreis (Heating Circuit)

| Address | Attribute | Unit | Min | Max | Default | Name | Description |
|---------|-----------|------|-----|-----|---------|------|-------------|
| 150 | R | - | - | - | - | heizkreis_status | Status Heizkreis (see enum below) |
| 151 | R | °C | - | - | - | heizkreis_ist | Isttemperatur Heizkreis |
| 152 | R | °C | - | - | - | heizkreis_soll | Solltemperatur Heizkreis (0–85 °C) |
| 153 | R | - | - | - | - | heizkreis_betriebsmodus | Betriebsmodus (0=Aus, 1=Heizen, 2=Kühlen) |
| 154 | R/W | - | - | - | 0 | heizkreis_betriebsart | Betriebsart (0=Auto, 1=Heizen) |
| 155 | R/W | - | - | - | 2 | heizkreis_energiemodus | Energiemodus (see enum below) |
| 156 | R/W | K | -5 | 5 | 0 | heizkurve_parallelverschiebung | Parallelverschiebung Heizkurve |
| 157 | R/W | - | - | - | 0 | saisonauswahl_manuell | Manuelle Saisonauswahl (see enum below) |
| 158 | R/W | °C | 0 | 50 | 18 | sommerbetrieb_heizen_aus | Sommerbetrieb (Heizen Aus) |
| 159 | R/W | °C | 0 | 50 | 16 | winterbetrieb_heizen_ein | Winterbetrieb (Heizen Ein) |
| 160 | R/W | °C | 0 | 50 | 22 | kuehlbetrieb_ein | Kühlbetrieb Ein |
| 161 | R/W | °C | 0 | 50 | 20 | kuehlbetrieb_aus | Kühlbetrieb Aus |
| 162 | R | - | - | - | - | sommerbetrieb_aktiv | Sommerbetrieb aktiv (0=Nein, 1=Ja) |
| 163 | R | - | - | - | - | kuehlbetrieb_aktiv | Kühlbetrieb aktiv (0=Nein, 1=Ja) |

**Heizkreis Status Enum (Address 150):**
- 0: Aus
- 1: Heizen
- 2: Kühlen
- 3: Taupunkt
- 4: Pumpenwartungslauf
- 5: Frostschutz
- 6: Handbetrieb
- 7: Testmodus
- 8: Initialisierung
- 9: Sicherheitszustand

**Energiemodus Enum (Address 155):**
- 0: Off
- 1: Eco
- 2: Normal
- 3: Comfort
- 4: Benutzerdefiniert

**Saisonauswahl Enum (Address 157):**
- 0: Auto
- 1: Heizen
- 2: Kühlen
- 3: Aus

#### Externer Wärmeerzeuger (External Heat Generator)

| Address | Attribute | Unit | Default | Name | Description |
|---------|-----------|------|---------|------|-------------|
| 200 | R | - | - | status_ext_wez_heizen | Status externer Wärmeerzeuger Heizen |
| 201 | R/W | - | 0 | betriebsart_ext_wez_heizen | Betriebsart ext. WEZ Heizen (see enum below) |
| 202 | R | - | - | status_ext_wez_twe | Status externer Wärmeerzeuger TWE |
| 203 | R/W | - | 0 | betriebsart_ext_wez_twe | Betriebsart ext. WEZ TWE (see enum below) |

**Betriebsart ext. WEZ Enum (Addresses 201, 203):**
- 0: Auto
- 1: Nur WP
- 2: Beide
- 3: Sekundärer WEZ

**Status ext. WEZ Status Codes:**
- 0: keine Anforderung
- 100: Anforderung
- 200: Bereitschaft Auto Parallel
- 201: Bereitschaft Auto Alternativ
- 204: Bereitschaft wg. Störung
- 205: Bereitschaft Handbetrieb Parallel
- 206: Bereitschaft wg. Handbetrieb Parallel
- 207: Bereitschaft EVU Sperre
- 300: Anforderung Auto Parallel
- 301: Anforderung Auto Alternativ
- 304: Anforderung wg. Störung
- 305: Anforderung Handbetrieb Parallel
- 306: Anforderung wg. Handbetrieb Parallel
- 307: Anforderung EVU Sperre

#### Temperaturfühler (Temperature Sensors)

| Address | Attribute | Unit | Name | Description |
|---------|-----------|------|------|-------------|
| 250 | R | °C | t1_temp | T1 (X13) Temperaturfühler |
| 251 | R | °C | t2_temp | T2 (X12) Temperaturfühler |
| 252 | R | °C | t3_temp | T3 (X11) Temperaturfühler |
| 253 | R | °C | t4_temp | T4 (X10) Temperaturfühler |
| 254 | R | °C | aussentemperatur | Außentemperatur |
| 255 | R | °C | aussentemperatur_gemittelt | Gemittelte Außentemperatur |

#### Betriebsstunden (Operating Hours)

| Address | Attribute | Unit | Min | Max | Name | Description |
|---------|-----------|------|-----|-----|------|-------------|
| 300 | R | h | 0 | 65535 | bh_heizkreispumpe | Heizkreispumpe Laufzeit |
| 301 | R | h | 0 | 65535 | bh_ext_wez | Externer Wärmeerzeuger Laufzeit |

---

### 3. Universalmodul (Universal Module)

**Unit ID:** 30

#### Register Map

| Address | Attribute | Unit | Min | Max | Default | Name | Description |
|---------|-----------|------|-----|-----|---------|------|-------------|
| 150 | R | - | - | - | - | heizkreis_status | Status Heizkreis (see enum below) |
| 151 | R | °C | - | - | - | heizkreis_ist | Isttemperatur Heizkreis |
| 152 | R | °C | - | - | - | heizkreis_soll | Solltemperatur Heizkreis (0–85 °C) |
| 153 | R | - | - | - | - | betriebsmodus | Betriebsmodus (0=Aus, 1=Heizen, 2=Kühlen) |
| 154 | R/W | - | - | - | 0 | betriebsart | Betriebsart (0=Auto, 1=Aus) |
| 155 | R/W | - | - | - | 2 | energiemodus | Energiemodus (see enum below) |
| 156 | R/W | K | -5 | 5 | 0 | heizkurve_parallelverschiebung | Parallelverschiebung Kurve |
| 157 | R/W | - | - | - | 0 | saisonauswahl_manuell | Manuelle Saisonauswahl (see enum below) |
| 158 | R/W | °C | 0 | 50 | 18 | sommerbetrieb_heizen_aus | Sommerbetrieb (Heizen Aus) |
| 159 | R/W | °C | 0 | 50 | 16 | winterbetrieb_heizen_ein | Winterbetrieb (Heizen Ein) |
| 160 | R/W | °C | 0 | 50 | 22 | kuehlbetrieb_ein | Kühlbetrieb Ein |
| 161 | R/W | °C | 0 | 50 | 20 | kuehlbetrieb_aus | Kühlbetrieb Aus |
| 162 | R | - | - | - | - | sommerbetrieb_aktiv | Sommerbetrieb aktiv (0=Nein, 1=Ja) |
| 163 | R | - | - | - | - | kuehlbetrieb_aktiv | Kühlbetrieb aktiv (0=Nein, 1=Ja) |

**Heizkreis Status Enum (Address 150):**
- 0: Aus
- 1: Heizen
- 2: Kühlen
- 3: Taupunkt
- 4: Pumpenwartungslauf
- 5: Frostschutz
- 6: Handbetrieb
- 7: Testmodus
- 8: Initialisierung
- 9: Sicherheitszustand

**Energiemodus Enum (Address 155):**
- 0: Off
- 1: Eco
- 2: Normal
- 3: Comfort
- 4: Benutzerdefiniert

**Saisonauswahl Enum (Address 157):**
- 0: Auto
- 1: Heizen
- 2: Kühlen
- 3: Aus

#### Temperaturfühler (Temperature Sensors)

| Address | Attribute | Unit | Name | Description |
|---------|-----------|------|------|-------------|
| 250 | R | °C | t1_temp | T1 (X9) Temperaturfühler |
| 251 | R | °C | t2_temp | T2 (X10) Temperaturfühler |
| 252 | R | °C | t3_temp | T3 (X11) Temperaturfühler |
| 253 | R | °C | t4_temp | T4 (X12) Temperaturfühler |

#### Betriebsstunden (Operating Hours)

| Address | Attribute | Unit | Min | Max | Name | Description |
|---------|-----------|------|-----|-----|------|-------------|
| 300 | R | h | 0 | 65535 | bh_heizkreispumpe | Heizkreispumpe Laufzeit |

---

## Data Type Notes

- All temperature values are transmitted as signed 16-bit integers (INT16) in units of 0.1°C
  - Example: A value of 235 represents 23.5°C
- Power values (kW) are transmitted as unsigned 16-bit integers in units of 0.01 kW
  - Example: A value of 315 represents 3.15 kW
- COP values are transmitted as unsigned 16-bit integers in units of 0.01
  - Example: A value of 425 represents 4.25
- Flow rate values are transmitted as unsigned 16-bit integers in units of 0.1 l/min
- Operating hours are transmitted as unsigned 16-bit integers in hours
- Enum values are transmitted as unsigned 16-bit integers

## Connection Parameters

- Modbus Protocol: RTU or TCP
- Default Baud Rate (RTU): 9600, 8N1
- Default TCP Port: 502
