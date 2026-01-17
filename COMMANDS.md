# STRIDE Command Reference

All commands assume you're in the STRIDE repository root with venv activated:

```bash
cd /Users/arnoclaude/Documents/TUM/Thesis/STRIDE
source venv/bin/activate
```

---

## Config Chaining System

Configs are now chained in order: `base.yaml` → `depot` → `scenario/sensitivity`

### Basic Usage

```bash
# Schmid base run (base + depot)
python3 -m multi_stage.main -c configs/base.yaml configs/depots/schmid.yaml -s inputs/schmid/scenarios/base.csv --name schmid_base

# With scenario override
python3 -m multi_stage.main -c configs/base.yaml configs/depots/schmid.yaml configs/scenarios/optimistic.yaml -s inputs/schmid/scenarios/base.csv --name schmid_optimistic

# With sensitivity override
python3 -m multi_stage.main -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/wacc_high.yaml -s inputs/schmid/scenarios/base.csv --name schmid_wacc_high
```

---

## Schmid Depot Runs

### Base Case

```bash
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_base
```

### Scenarios

```bash
# Pessimistic (no CO2 constraint, constant grid)
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/scenarios/pessimistic.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_pessimistic

# Optimistic (1.5C pathway, CAP grid)
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/scenarios/optimistic.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_optimistic
```

### Sensitivity Analysis

```bash
# WACC
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/wacc_low.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_wacc_low

python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/wacc_high.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_wacc_high

# PV CAPEX
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/pv_capex_low.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_pv_low

python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/pv_capex_high.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_pv_high

# ESS CAPEX
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/ess_capex_low.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_ess_low

python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/ess_capex_high.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_ess_high

# CO2 factor
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/co2_factor_low.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_co2_low

python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/co2_factor_high.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_co2_high

# Charger CAPEX
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/charger_capex_low.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_charger_low

python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/charger_capex_high.yaml \
    -s inputs/schmid/scenarios/base.csv --name schmid_charger_high
```

---

## Metzger Depot Runs

```bash
# Base case
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/metzger.yaml \
    -s inputs/metzger/scenarios/base.csv \
    --name metzger_base

# With scenario
python3 -m multi_stage.main \
    -c configs/base.yaml configs/depots/metzger.yaml configs/scenarios/optimistic.yaml \
    -s inputs/metzger/scenarios/base.csv \
    --name metzger_optimistic
```

---

## Visualization Commands

```bash
# Generate plots for a run
python3 -m multi_stage.visualize runs/schmid_base --png --pdf

# Compare scenarios
python3 -m multi_stage.compare \
    runs/schmid_pessimistic runs/schmid_base runs/schmid_optimistic \
    -o analysis/schmid/scenarios
```

---

## Quick Checks

```bash
# Verify config chaining works
python3 -c "
from multi_stage.config_loader import MultiStageConfig
c = MultiStageConfig.from_yaml_chain(['configs/base.yaml', 'configs/depots/schmid.yaml'])
print(f'Fleet: {c.demand_base_num_vehicles}, WACC: {c.wacc}, Pathway: {c.emissions_pathway_type}')
"

# List configs
find configs -name "*.yaml" | sort

# Check venv
which python3

# List runs
ls -lt runs/ | head -10
```

---

## Directory Structure

```
configs/
├── base.yaml              # Complete shared defaults (source of truth)
├── depots/
│   ├── schmid.yaml        # fleet=84, CO2 baseline, paths
│   └── metzger.yaml       # fleet=18, CO2 baseline, paths
├── scenarios/
│   ├── pessimistic.yaml   # No CO2 constraint, constant grid
│   └── optimistic.yaml    # 1.5C pathway, CAP grid
└── sensitivity/
    ├── wacc_low.yaml      # 2.5%
    ├── wacc_high.yaml     # 5.3%
    ├── pv_capex_*.yaml    # 0.90/1.60 €/Wp
    ├── ess_capex_*.yaml   # 0.45/0.80 €/Wh
    ├── co2_factor_*.yaml  # 0.25/0.45 kg/kWh
    └── charger_capex_*.yaml # 25kW/350kW
```
