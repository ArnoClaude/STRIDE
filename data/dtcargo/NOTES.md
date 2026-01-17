# DTCargo Driving Data

> Last updated: 2026-01-17

---

## Overview

Source driving data for STRIDE simulation from Schmid freight forwarding depot in Bavaria.

- **Vehicles:** 83 trucks (regional freight distribution)
- **Data period:** October 2024 (50 days)
- **Data type:** GPS/telematics daily driving profiles

---

## Data Representativeness

### Justification for 50-Day → 180-Day Extrapolation

**Claim:** One month of regional freight driving data can be extrapolated to represent longer periods for investment planning purposes.

**Core argument:** Regional freight trucks have **predictable, contract-driven routes**. What varies seasonally is energy consumption (±15-20%), not driving patterns.

### Evidence

#### 1. Depot-Based Operations Have Predictable Patterns

> "Vehicles that originate from a consistent depot each day"
>
> — Bruchon et al. (2024), NREL

**Source:** Bruchon, M., Borlaug, B., Liu, B., Jonas, T., Sun, J., Le, N., & Wood, E. (2024). "National Summary Statistics for Depot-Based Medium- and Heavy-Duty Vehicle Operations." NREL Data Catalog.
- URL: https://data.nrel.gov/submissions/231
- Technical report: NREL/TP-5400-88241

NREL Fleet DNA database shows "daily drive cycle is often driven by its application" — vocation determines pattern, not season.

#### 2. Regional Freight = Predictable Routes

> "Short-haul operations are early candidates for plug-in electric vehicles given their short, **predictable routes and return-to-base applications**, which allows vehicles to recharge when off shift at their depots."
>
> — Borlaug et al. (2021), Nature Energy

**Source:** Borlaug, B., Muratori, M., Gilleran, M., Woody, D., Muston, W., Canada, T., Ingram, A., Gresham, H., & McQueen, C. (2021). Heavy-duty truck electrification and the impacts of depot charging on electricity distribution systems. *Nature Energy*, 6(6), 673–682.
- DOI: https://doi.org/10.1038/s41560-021-00855-0
- File: `sources/borlaug_2021_nature_energy.pdf`

#### 3. 70-90% of Regional Trucks Return to Depot Daily

> "In regional delivery transport, it is common for BET to spend long periods at night in the depot, which can then be used for battery charging."
>
> — T&E/Fraunhofer ISI (2025), p. 41

> "70% of UK electric trucks currently return to the depot overnight to charge."
>
> — T&E/Fraunhofer ISI (2025), p. 72

**Source:** Transport & Environment / Fraunhofer ISI / Oeko-Institut (2025). "Truck Depot Charging: Final Report." February 2025.
- File: `../grid_co2/sources/te_truck_depot_charging_2025.pdf`

### What Does and Does Not Vary Seasonally

| Factor | Seasonal Variation | Impact on STRIDE |
|--------|-------------------|------------------|
| **Energy consumption** | ±15-20% (HVAC, battery efficiency) | Conservative: October = moderate temps |
| **Route structure** | Minimal (contract-driven) | Negligible |
| **Daily mileage** | Minimal for regional | Negligible |
| **Return-to-depot pattern** | Stable (70-90% daily) | None |

### October Representativeness

October is suitable as a representative month:
- **Moderate temperatures:** Neither winter (high heating load) nor summer (high A/C load)
- **No holiday season:** Not affected by Christmas/year-end freight peaks
- **No produce season:** Not affected by agricultural peak periods
- **Typical operations:** Post-summer, pre-holiday normal operations

### Acknowledged Limitation

Energy consumption varies ±15-20% seasonally due to cabin HVAC and battery efficiency in cold weather. For investment planning purposes (infrastructure sizing), route stability is the primary factor — seasonal energy variation is captured by using conservative demand assumptions.

---

## Sources

| File | Description |
|------|-------------|
| `sources/borlaug_2021_nature_energy.pdf` | Borlaug et al. (2021) Nature Energy - depot charging, predictable routes |
| `../grid_co2/sources/te_truck_depot_charging_2025.pdf` | T&E/Fraunhofer (2025) - 70-90% depot return rate |

### External References

| Citation | URL/DOI |
|----------|---------|
| Bruchon et al. (2024) NREL depot operations | https://data.nrel.gov/submissions/231 |
| Borlaug et al. (2021) Nature Energy | https://doi.org/10.1038/s41560-021-00855-0 |
| NREL Fleet DNA database | https://www.nrel.gov/transportation/fleettest-fleet-dna |

---

## Data Processing

See `helper.py` for data processing scripts.

- `raw/` - Original data files
- `processed/` - Cleaned data for STRIDE input
