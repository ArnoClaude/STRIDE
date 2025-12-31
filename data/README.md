# STRIDE Data Directory

> Last updated: 2025-12-31

---

## Current Status

**Phase 2 COMPLETE**: Single-stage REVOL-E-TION test run successful with Schmid data (84 vehicles).

**Next**: Phase 3 - Two-stage multi-stage test

See `.claude/plans/schmid_multi_stage.md` for detailed execution plan.

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
| `grid_connection_capex/` | Grid upgrade costs | ✅ Complete | - |
| `charger_capex/` | Charger costs | ✅ Complete | - |
| `peak_demand_charges/` | Leistungspreis (€/kW/a) | ✅ Complete | - |
| `financial_params/` | Discount rate, lifespans | ✅ Complete | - |
| `fixed_demand/` | Depot base load | ✅ Using Franziska's data | - |
| `depot_locations/` | Lat/lon coordinates | ✅ Augsburg (Schmid) | - |
| `physical_constraints/` | Roof area, space limits | ⏭️ Skipped (not binding) | Low |
| `co2_pathway/` | CO2 reduction targets | 🔴 TODO | Low |

---

## REVOL-E-TION Input Files

Ready-to-use input files in `revoletion/example_schmid/`:

| File | Description | Status |
|------|-------------|--------|
| `bev_log_test.csv` | 84 vehicles, 50 days | ✅ |
| `bev_log_prod.csv` | 84 vehicles, 150 days | ✅ |
| `dem_timeseries_test.csv` | Fixed demand, 50 days | ✅ |
| `dem_timeseries_prod.csv` | Fixed demand, 150 days | ✅ |
| `scenarios_schmid_test.csv` | Full scenario config | ✅ |
| `settings.csv` | REVOL-E-TION settings | ✅ |

---

## Test Run Results (2025-12-31)

Single-stage test with 84 vehicles, 50 days:

| Metric | Value |
|--------|-------|
| Runtime | 514s (~8.5 min) |
| NPC | 29.7M EUR |
| Renewable Share | 64.1% |
| PV installed | 1,841 kW |
| Grid capacity | 1,684 kW |

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
