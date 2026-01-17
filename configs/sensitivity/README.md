# Sensitivity Analysis Configurations

Minimal override files - each changes ONE parameter from base.yaml.

## Usage

```bash
# Chain: base + depot + sensitivity
python -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/wacc_high.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_wacc_high
```

## Parameters

| File | Parameter | Base | Test | Source |
|------|-----------|------|------|--------|
| wacc_low.yaml | economics.wacc | 0.035 | 0.025 | Favorable financing |
| wacc_high.yaml | economics.wacc | 0.035 | 0.053 | Fraunhofer nominal |
| pv_capex_low.yaml | pv.base_cost_per_w | 1.00 | 0.90 | Fraunhofer niedrig |
| pv_capex_high.yaml | pv.base_cost_per_w | 1.00 | 1.60 | Fraunhofer hoch |
| ess_capex_low.yaml | ess.base_cost_per_wh | 0.50 | 0.45 | Fraunhofer niedrig |
| ess_capex_high.yaml | ess.base_cost_per_wh | 0.50 | 0.80 | Fraunhofer hoch |
| co2_factor_low.yaml | grid.co2_spec_g2s | 0.35 | 0.25 | Optimistic grid |
| co2_factor_high.yaml | grid.co2_spec_g2s | 0.35 | 0.45 | Nighttime charging |
| charger_capex_low.yaml | bev.capex_charger | 20000 | 5000 | 25 kW DC |
| charger_capex_high.yaml | bev.capex_charger | 20000 | 29000 | 350 kW DC |

