# STRIDE Data Directory

> Last synced with Data Collection II.csv: 2025-12-28

---

## Status Overview

| Folder | Description | Status | Priority |
|--------|-------------|--------|----------|
| `depot_Schmid/` | Fleet data (84 trucks) | ✅ Complete | - |
| `depot_Metzger/` | Fleet data (18 trucks) | ✅ Complete | - |
| `dtcargo/` | Raw tracks data | ✅ Complete | - |
| `grid_g2s/` | Grid import prices (SMARD) | ✅ Complete | - |
| `grid_s2g/` | Grid export prices (Marktwert Solar) | ✅ Complete | - |
| `pv_capex/` | PV costs + projections | ✅ Complete | - |
| `ess_capex/` | Battery costs + projections | ✅ Complete | - |
| `grid_co2/` | Grid CO2 factors | ✅ Complete | - |
| `grid_connection_capex/` | Grid upgrade costs | 🔴 TODO | Medium |
| `charger_capex/` | Charger costs | 🔴 TODO | Medium |
| `peak_demand_charges/` | Leistungspreis (€/kW/a) | 🔴 TODO | Medium |
| `fixed_demand/` | Depot base load | 🔴 TODO (waiting depot) | HIGH |
| `depot_locations/` | Lat/lon coordinates | 🔴 TODO (waiting depot) | Medium |
| `physical_constraints/` | Roof area, space limits | 🔴 TODO (waiting depot) | Medium |
| `financial_params/` | Discount rate, lifespans | 🔴 TODO | Medium |
| `co2_pathway/` | CO2 reduction targets | 🔴 TODO | Medium |

---

## CSV Reconciliation

From "Data Collection II.csv" (35 items):
- ✅ **Covered by folders**: 16 items (existing + newly created)
- ⏭️ **Grouped** into other folders: 6 items (num vehicles, charging power, battery capacity, lifespans, embodied emissions, etc.)
- ⏭️ **Omitted** (done/low priority/out of scope): 12 items (BRS, vehicle glider, battery chemistry, aging model, efficiency, SDR, timezone, holidays, validation data)
- ❓ **Not covered**: 1 item (O&M costs - typically 1-2% of CAPEX, low variability)

---

## Folder Structure

Each data folder should contain:
```
folder_name/
├── NOTES.md          # Data values, sources, methodology
└── sources/          # Downloaded PDFs, CSVs, etc.
```

---

## Blocking Items

These require depot response:
1. **Fixed electrical demand** - base load profile
2. **Depot coordinates** - lat/lon for PVGIS
3. **Physical constraints** - roof area for PV

---

## Data Collection CSV

Master requirements tracked in:
`/Thesis/Arno Claude Master's Thesis - Data Collection II.csv`
