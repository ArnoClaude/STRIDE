# Depot Configurations

Depot-specific overrides for fleet size, CO2 baseline, and file paths.

## Usage

```bash
# Always chain with base.yaml first
python -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_base
```

## Depots

| File | Fleet | CO2 Baseline | Settings Path |
|------|-------|--------------|---------------|
| schmid.yaml | 84 | 200,000 kg | inputs/schmid/settings.csv |
| metzger.yaml | 18 | 45,000 kg | inputs/metzger/settings.csv |

## What's Depot-Specific

- `demand.base_num_vehicles` - Fleet size
- `emissions.base_limit_kg` - CO2 baseline for pathway calculation
- `revoletion.settings_path` - Path to REVOL-E-TION settings

Everything else (technology costs, WACC, pathways) is shared via base.yaml.
