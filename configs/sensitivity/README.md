# Sensitivity Analysis Configurations

This folder contains config files for one-at-a-time (OAT) sensitivity analysis.

Each config is a complete copy of the base case (`schmid_6stage.yaml`) with **one parameter changed**.

## Usage

```bash
# Run individual sensitivity
python3 -m multi_stage.main -c configs/sensitivity/wacc_high.yaml -s inputs/schmid/scenarios.csv

# Run all sensitivities (batch)
for config in configs/sensitivity/*.yaml; do
    name=$(basename "$config" .yaml)
    python3 -m multi_stage.main -c "$config" -s inputs/schmid/scenarios.csv -o "outputs/sensitivity/$name"
done
```

## Sensitivity Cases

| File | Parameter | Base Value | Test Value | Rationale |
|------|-----------|------------|------------|-----------|
| `wacc_low.yaml` | economics.wacc | 0.035 | 0.025 | Lower bound: favorable financing |
| `wacc_high.yaml` | economics.wacc | 0.035 | 0.057 | Upper bound: Fraunhofer nominal WACC |
| `co2_factor_low.yaml` | co2_spec_g2s | 0.35 | 0.25 | Optimistic grid decarbonization |
| `co2_factor_high.yaml` | co2_spec_g2s | 0.35 | 0.45 | Conservative (more coal in mix) |

## Base Case Reference

All sensitivity configs derive from: `configs/schmid_6stage.yaml`

Key base case parameters:
- WACC: 3.5% (Fraunhofer real WACC)
- CO2 factor: 0.35 kg/kWh (German grid 2023)
- PV cost decline: 3%/yr
- ESS cost decline: 5%/yr
- Fleet growth: 2%/yr

## Notes

- Each config is self-contained (no inheritance mechanism yet)
- Output folders should match config names for traceability
- Compare results using `multi_stage.compare_sensitivity` (TODO)
