# Scenario Configurations

Complete storylines about the future - different from sensitivities.

## Usage

```bash
# Chain: base + depot + scenario
python -m multi_stage.main \
    -c configs/base.yaml configs/depots/schmid.yaml configs/scenarios/optimistic.yaml \
    -s inputs/schmid/scenarios/base.csv \
    --name schmid_optimistic
```

## Scenarios

| File | Grid CO2 2050 | CO2 Pathway | Description |
|------|---------------|-------------|-------------|
| (base.yaml) | 0.182 kg/kWh | WB2C 2.5%/yr | BAU - current trajectory |
| pessimistic.yaml | 0.350 kg/kWh | None | No decarbonization |
| optimistic.yaml | 0.029 kg/kWh | 1.5C 4.2%/yr | Aggressive climate action |

## Sources

- Grid trajectories: Seckinger & Radgen (2021), Energies 14(9):2527
- CO2 pathway: SBTi Corporate Net-Zero Standard V2.0

