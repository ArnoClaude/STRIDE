# Depot Schmid - BEV Usage Data

## Overview

This folder contains BEV (Battery Electric Vehicle) usage logs for Spedition Schmid, derived from DT-Cargo telematics data.

---

## Data Source

### DT-Cargo Telematics Dataset
- **Provider:** DT-Cargo / TUM FTM research project
- **Raw File:** `dtcargo/raw/tracks_with_energy.csv`
- **Filter:** `freight_forwarder = 6` (Schmid)
- **Time Period:** June 2023 - February 2024 (~249 days)
- **Data Type:** GPS tracks with energy consumption estimates

**Note:** Schmid's data is from a different time period than Metzger (2021-2022). The simulation dates are adjusted accordingly.

### Depot Information
| Property | Value |
|----------|-------|
| Freight Forwarder ID | 6 |
| Name | Schmid |
| Number of Vehicles | 97 |
| Location | Bavaria, Germany |

---

## Transformation Process

### Input
- `tracks_with_energy.csv` - Trip records with:
  - `vehicle_id` - Vehicle identifier
  - `start_time`, `stop_time` - Trip timestamps
  - `distance_km` - Trip distance
  - `home_base` - Boolean flag if trip ends at depot
  - `energy_consumption_kwh` - Estimated energy consumption
  - `avg_energy_consumption_kwh/km_cleaned` - Specific consumption

### Output
- `bev_log.csv` - REVOL-E-TION compatible BEV usage log
- 15-minute intervals
- Multi-index columns: `bevN` → `[atbase, dsoc, consumption, atac, atdc, tour_dist]`

### Column Definitions

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `atbase` | bool | - | Vehicle is at depot (available for charging) |
| `dsoc` | int | % | Delta SOC (always 0, not used) |
| `consumption` | float | W | Power consumption during interval |
| `atac` | bool | - | External AC charging available |
| `atdc` | bool | - | External DC charging available |
| `tour_dist` | float | m | Distance traveled (set in first interval of trip) |

### Consumption Calculation
```
consumption_W = energy_consumption_kwh * 1000 / 0.25
```
- Energy is distributed proportionally across 15-min intervals overlapping with each track
- If `energy_consumption_kwh` is missing, fallback to average specific consumption × distance

### atbase Logic
- Set to `True` for all intervals between a trip ending at `home_base=True` and the next trip start
- Represents when vehicle is at depot and available for charging

---

## Usage

```bash
# Generate 7-day test
python transform.py --days 7

# Generate full year (default)
python transform.py

# Custom start date and duration
python transform.py --start 2021-09-10 --days 365
```

**Note:** Schmid has 97 vehicles, so processing takes longer than Metzger (18 vehicles).

---

## Vehicle Mapping

The transform creates sequential BEV labels (bev0, bev1, ..., bev96) mapped from actual vehicle IDs.

Due to the large fleet size (97 vehicles), the actual vehicle_id to bevN mapping is dynamic based on sorted unique vehicle IDs in the dataset.

---

## Data Quality Notes

1. **Energy consumption estimates** are model-based (not measured). The `tracks_with_energy.csv` was pre-processed by Anna using an energy consumption model.

2. **Missing data**: Some tracks may have empty `energy_consumption_kwh`. Fallback uses average specific consumption from the dataset.

3. **Home base detection**: Based on GPS clustering in original DT-Cargo processing. May not be 100% accurate.

4. **External charging flags** (`atac`, `atdc`): Set to `True` for all intervals (assumption: external charging always available during trips).

5. **Large fleet considerations**: With 97 vehicles, the bev_log.csv will have 97×6 = 582 data columns plus time column. This may impact REVOL-E-TION solving time.

---

## Files

### Input (from dtcargo/raw/)
- `tracks_with_energy.csv` - Shared source file

### Output (processed/)
- `bev_log.csv` - REVOL-E-TION compatible BEV usage log

---

## References

1. DT-Cargo Research Project, TUM FTM
2. Anna's helper.py for BEV log generation logic
3. REVOL-E-TION documentation: https://github.com/TUMFTM/REVOL-E-TION

---

## Open Items

- [ ] **Validate against depot operator feedback**: Confirm vehicle count and typical schedules with Schmid
- [ ] **dem_timeseries.csv**: Fixed depot demand (buildings, lights, etc.) not yet available - need from depot operator
- [ ] **Fleet subset**: Consider if full 97-vehicle simulation is needed or if a representative subset would suffice for computational tractability
