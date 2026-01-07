# Sensitivity Analysis Configurations

This folder contains config files for one-at-a-time (OAT) sensitivity analysis.

Each config is a complete copy of the base case (`schmid_6stage.yaml`) with **one parameter changed**.

## Usage

```bash
# Run individual sensitivity
python3 -m multi_stage.main -c configs/sensitivity/wacc_high.yaml -s inputs/schmid/scenarios.csv -o outputs/sensitivity/schmid/wacc_high

# Run all sensitivities (batch)
for config in configs/sensitivity/*.yaml; do
    name=$(basename "$config" .yaml)
    python3 -m multi_stage.main -c "$config" -s inputs/schmid/scenarios.csv -o "outputs/sensitivity/schmid/$name"
done
```

## Sensitivity Cases

| File | Parameter | Base Value | Test Value | Source |
|------|-----------|------------|------------|--------|
| `wacc_low.yaml` | economics.wacc | 0.035 | 0.025 | Favorable financing assumption |
| `wacc_high.yaml` | economics.wacc | 0.035 | 0.057 | Fraunhofer LCOE Table 2, nominal WACC |
| `co2_factor_low.yaml` | co2_spec_g2s | 0.35 | 0.25 | Optimistic grid decarbonization |
| `co2_factor_high.yaml` | co2_spec_g2s | 0.35 | 0.45 | Conservative (more coal in mix) |
| `pv_capex_low.yaml` | pv.base_cost_per_w | 1.00 | 0.90 | Fraunhofer LCOE Tabelle 1, "niedrig" |
| `pv_capex_high.yaml` | pv.base_cost_per_w | 1.00 | 1.60 | Fraunhofer LCOE Tabelle 1, "hoch" |
| `ess_capex_low.yaml` | ess.base_cost_per_wh | 0.50 | 0.45 | Fraunhofer LCOE Tabelle 1, "niedrig" |
| `ess_capex_high.yaml` | ess.base_cost_per_wh | 0.50 | 0.80 | Fraunhofer LCOE Tabelle 1, "hoch" |

## Base Case Reference

All sensitivity configs derive from: `configs/schmid_6stage.yaml`

Key base case parameters:
- WACC: 3.5% (Fraunhofer real WACC)
- CO2 factor: 0.35 kg/kWh (German grid 2024)
- PV CAPEX: 1.00 €/Wp
- ESS CAPEX: 0.50 €/Wh
- PV cost decline: 3%/yr
- ESS cost decline: 5%/yr
- Fleet growth: 2%/yr

## Notes

- Each config is self-contained (no inheritance mechanism)
- Output folders should match config names for traceability
- CO2 factor sensitivity requires modified scenario CSV files (`scenarios_co2_low.csv`, `scenarios_co2_high.csv`)
- Compare results using `python3 -m multi_stage.compare_sensitivity`

## Documentation

See `data/sensitivity_analysis/NOTES.md` for full methodology and source citations.
