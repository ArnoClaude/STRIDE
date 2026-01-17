# Scenario Configurations

> Last updated: 2026-01-16

---

## Overview

Scenarios represent **complete storylines** about the future — different from sensitivities which vary single parameters. Each scenario combines:

1. **Grid CO2 factor trajectory** (how fast the grid decarbonizes)
2. **CO2max pathway** (depot emission constraints using SBTi ACA)
3. **Technology cost trajectories** (PV/ESS decline rates)
4. **Economic parameters** (WACC reflecting policy support level)

---

## Three Scenarios

| Scenario | Grid CO2 by 2050 | CO2 Reduction | Storyline |
|----------|------------------|---------------|-----------|
| **Pessimistic** | 0.35 kg/kWh (constant) | None | Grid decarbonization fails; no depot constraints |
| **Moderate** | 0.182 kg/kWh (-74%) | SBTi WB2C (2.5%/yr) | BAU scenario from Seckinger & Radgen (2021) |
| **Optimistic** | 0.029 kg/kWh (-95%) | SBTi 1.5C (4.2%/yr) | CAP scenario with aggressive targets |

---

## Grid CO2 Factor Trajectories

**Source:** Seckinger, N., & Radgen, P. (2021). "Dynamic Prospective Average and Marginal GHG Emission Factors—Scenario-Based Method for the German Power System until 2050." *Energies*, 14(9), 2527.
**DOI:** https://doi.org/10.3390/en14092527
**File:** `data/grid_co2/sources/energies-14-02527.pdf`

### Values from Paper (Table 2, Figure 4)

| Year | Pessimistic | Moderate (BAU) | Optimistic (CAP) |
|------|-------------|----------------|------------------|
| 2025 | 0.350 | 0.350 | 0.350 |
| 2030 | 0.350 | 0.300 | 0.250 |
| 2035 | 0.350 | 0.260 | 0.150 |
| 2040 | 0.350 | 0.220 | 0.080 |
| 2045 | 0.350 | 0.200 | 0.050 |
| 2050 | 0.350 | 0.182 | 0.029 |

**Notes:**
- Pessimistic: No grid decarbonization (constant 2024 value)
- Moderate (BAU): -74% reduction vs 1990, 57% renewables by 2050
- Optimistic (CAP): -95% reduction vs 1990, 92% renewables by 2050

---

## CO2max Pathway (SBTi ACA)

### Source Documents

1. **SBTi Corporate Near-Term Criteria v5.3** (September 2025)
   - File: `data/co2_pathway/sources/SBTi-criteria.pdf`
   - URL: https://files.sciencebasedtargets.org/production/files/SBTi-criteria.pdf
   - **Criterion NT-C15**: "At a minimum, scope 1 and scope 2 targets shall be consistent with the level of decarbonization required to keep global temperature increase to 1.5°C compared to pre-industrial temperatures."

2. **SBTi Target-Setting Methods Documentation**
   - File: `data/co2_pathway/sources/SBTi-Documentation-of-target-setting-methods.pdf`
   - URL: https://files.sciencebasedtargets.org/production/files/Documentation-of-target-setting-methods.pdf
   - **Quote**: "The annual linear reduction must be at least **4.2%** for a 1.5°C objective or **2.5%** for a well-below 2°C objective."

### Absolute Contraction Approach (ACA)

The ACA applies a **linear annual reduction rate (LARR)** to absolute emissions:

```
E(t) = E(base) × [1 - LARR × (t - base_year)]
```

Where:
- `E(t)` = Emissions limit in year t
- `E(base)` = Baseline emissions (2025)
- `LARR` = Linear Annual Reduction Rate
- For 1.5°C: LARR = 4.2%/year
- For WB2C: LARR = 2.5%/year

**Source:** SBTi (2025). Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation, Equation 4.1, p. 25.

### Resulting Reduction Percentages

Calculated using formula: `Reduction = LARR × (t - 2025)`

| Year | Pessimistic | Moderate (WB2C, 2.5%) | Optimistic (1.5C, 4.2%) |
|------|-------------|----------------------|------------------------|
| 2025 | 0% | 0% | 0% |
| 2030 | 0% | 12.5% | 21% |
| 2035 | 0% | 25% | 42% |
| 2040 | 0% | 37.5% | 63% |
| 2045 | 0% | 50% | 84% |
| 2050 | 0% | 62.5% | 105% (→ net-zero) |

**Note:** With LARR=4.2%, the formula yields >100% reduction by 2050, meaning net-zero is reached before 2050 (at ~2049). The code caps at 0 kg.

---

## Usage

```bash
# Run a scenario
python -m multi_stage.main -c configs/scenarios/moderate.yaml -s inputs/schmid/scenarios/base.csv --name moderate_scenario

# Compare scenarios
python -m multi_stage.compare runs/pessimistic_scenario runs/moderate_scenario runs/optimistic_scenario -o analysis/schmid/scenarios
```

---

## File Structure

```
configs/scenarios/
├── README.md           # This file
├── pessimistic.yaml    # No decarbonization
├── moderate.yaml       # BAU trajectory
└── optimistic.yaml     # CAP trajectory (aggressive)
```
