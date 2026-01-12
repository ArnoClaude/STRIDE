# Schmid Depot Analysis

This folder contains comparison outputs and documentation for Schmid depot optimization runs.

## Folder Structure

```
analysis/schmid/
├── README.md                   # This file
└── comparison/                 # Cross-run comparison outputs
    ├── tornado_npv.png/pdf
    ├── tornado_capex.png/pdf
    ├── trajectory_*.png/pdf
    └── summary_table.csv
```

Actual run results are in `runs/` (flat structure):
```
runs/
├── base_run/
├── co2_low/
├── co2_high/
├── pv_capex_low/
├── pv_capex_high/
├── ess_capex_low/
├── ess_capex_high/
├── wacc_low/
└── wacc_high/
```

## Run Commands

All runs use the SAME base scenario file (`inputs/schmid/scenarios/base.csv`).
Sensitivity parameters are controlled via config files.

### Base Case
```bash
cd /Users/arnoclaude/Documents/TUM/Thesis/STRIDE
source venv/bin/activate

python -m multi_stage.main \
    --config configs/base/schmid_6stage.yaml \
    --scenario inputs/schmid/scenarios/base.csv \
    --name base_run \
    --type base
```

### Sensitivity Runs
```bash
# CO₂ factor sensitivity
python -m multi_stage.main -c configs/sensitivity/co2_factor_low.yaml -s inputs/schmid/scenarios/base.csv --name co2_low --type sensitivity
python -m multi_stage.main -c configs/sensitivity/co2_factor_high.yaml -s inputs/schmid/scenarios/base.csv --name co2_high --type sensitivity

# PV CAPEX sensitivity
python -m multi_stage.main -c configs/sensitivity/pv_capex_low.yaml -s inputs/schmid/scenarios/base.csv --name pv_capex_low --type sensitivity
python -m multi_stage.main -c configs/sensitivity/pv_capex_high.yaml -s inputs/schmid/scenarios/base.csv --name pv_capex_high --type sensitivity

# ESS CAPEX sensitivity
python -m multi_stage.main -c configs/sensitivity/ess_capex_low.yaml -s inputs/schmid/scenarios/base.csv --name ess_capex_low --type sensitivity
python -m multi_stage.main -c configs/sensitivity/ess_capex_high.yaml -s inputs/schmid/scenarios/base.csv --name ess_capex_high --type sensitivity

# WACC sensitivity
python -m multi_stage.main -c configs/sensitivity/wacc_low.yaml -s inputs/schmid/scenarios/base.csv --name wacc_low --type sensitivity
python -m multi_stage.main -c configs/sensitivity/wacc_high.yaml -s inputs/schmid/scenarios/base.csv --name wacc_high --type sensitivity
```

### Generate Comparison Visualizations
```bash
# Compare all sensitivity runs vs base
python -m multi_stage.compare runs/base_run runs/ -o analysis/schmid/comparison

# Compare single parameter (e.g., CO2)
python -m multi_stage.compare runs/base_run runs/co2_low runs/co2_high --pair co2 -o analysis/schmid/comparison

# Compare PV CAPEX
python -m multi_stage.compare runs/base_run runs/pv_capex_low runs/pv_capex_high --pair pv_capex -o analysis/schmid/comparison
```

## Sensitivity Parameters

| Parameter | Base | Low | High | Config Key |
|-----------|------|-----|------|------------|
| CO₂ factor | 0.35 kg/kWh | 0.25 | 0.45 | scenario_overrides.grid.co2_spec_g2s |
| PV CAPEX | 1.00 €/W | 0.90 | 1.10 | technology_costs.pv.base_cost_per_w |
| ESS CAPEX | 0.50 €/Wh | 0.40 | 0.60 | technology_costs.ess.base_cost_per_wh |
| WACC | 3.5% | 2.0% | 5.0% | economics.wacc |

## Architecture

**Config files** (`configs/`) define:
- Technology costs and learning curves
- WACC and economic parameters
- Emissions pathway (CO2 limits per stage)
- Scenario overrides (for sensitivity analysis)

**Scenario file** (`inputs/schmid/scenarios/base.csv`) defines:
- REVOL-E-TION block parameters (unchanging)
- Simulation setup (timestep, duration)
- Block-specific settings (charger power, efficiencies, etc.)

This separation means:
- ONE scenario file per depot
- Multiple configs for sensitivity analysis
- Configs can override scenario parameters via `scenario_overrides`

## Notes

- All runs use 50-day simulation (matches available BEV data)
- 1-hour timesteps (validated <1% difference from 15-min, 10x faster)
- 6 stages: 2025, 2030, 2035, 2040, 2045, 2050
- Schmid fleet: 84 vehicles (2025), growing to 137 (2050)
