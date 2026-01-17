# CO2 Pathway Data

> Last updated: 2026-01-16

---

## Summary

For a BEV depot, CO2 emissions are **Scope 2** (purchased electricity). Per GHG Protocol Scope 2 Guidance (2015):

```
CO2 (kg) = Energy consumed (kWh) × Grid emission factor (kg/kWh)
```

**Key insight:** The dominant CO2 source is imported electricity from the grid. On-site renewable generation (PV) and storage (ESS) reduce grid dependence, thereby reducing Scope 2 emissions. This is the primary mechanism that STRIDE models.

---

## Methodology: SBTi Absolute Contraction Approach (ACA)

STRIDE uses the **SBTi Absolute Contraction Approach** for depot CO2 pathway constraints.

### Source Documents

**Primary:**
1. Science Based Targets initiative (2025). "Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation (Revision), Version 1.0." March 2025.
   **File:** `sources/Documentation-of-target-setting-methods.pdf`
   **URL:** https://files.sciencebasedtargets.org/production/files/Documentation-of-target-setting-methods.pdf

2. Science Based Targets initiative (2025). "SBTi Corporate Near-Term Criteria V5.3." September 2025.
   **File:** `sources/SBTi-criteria.pdf`
   **URL:** https://sciencebasedtargets.org/resources/files/SBTi-criteria.pdf

3. Science Based Targets initiative (2019). "Foundations of Science-based Target Setting, Version 1.0." April 2019.
   **File:** `sources/foundations-of-SBT-setting.pdf`
   **URL:** https://sciencebasedtargets.org/resources/files/foundations-of-SBT-setting.pdf

---

## SBTi ACA Method

### Overview

The Absolute Contraction Approach (ACA) applies a **fixed annual reduction rate** to absolute emissions, irrespective of initial performance. All companies following ACA reduce emissions at the same rate.

> "The ACA produces an absolute emissions pathway between the base year and the target year, representing the company's idealized reduction curve. The ACA method determines interim performance values for scope 2 absolute emissions. Companies can then establish targets that ensure their scope 2 absolute emissions are reduced at a rate consistent with 1.5°C low or no overshoot scenarios."
>
> — SBTi (2025). Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation, p. 25

> "The method uses a grandfathering allocation principle which implies that the larger a company's emissions in a historic reference year, the larger its share of emissions in a desired target year."
>
> — SBTi (2025). Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation, p. 25

**What grandfathering means in practice:** Your future emissions budget is based on how much you emitted historically. If Company A emitted 1,000 tons in 2020 and Company B emitted 100 tons, then under a 50% reduction target, Company A gets 500 tons allowance while Company B only gets 50 tons. Both reduce by the same *percentage*, but the historically high emitter keeps a proportionally larger absolute budget. This is the simplest allocation method — everyone reduces at the same rate from their own baseline.

**Key characteristics:**
- Cross-sector method (applies to all industries)
- Grandfathering allocation principle
- Linear annual reduction over time
- Applicable to Scope 1, 2, and 3 emissions

### Formula

The target year emissions level is calculated using **Equation 4.1** from the SBTi Target-Setting Methods Documentation:

> **Equation 4.1. Calculating target year emissions level**
>
> CE_y = CE_by × [1 - LARR × (y - by)]
>
> Where:
> - CE_y = Company emissions in any year y within the target timeframe (t CO₂e)
> - CE_by = Company emissions in the base year selected by the company (t CO₂e)
> - y = Any year y within the target timeframe
> - by = The base year selected by the company
> - LARR = Linear annual reduction rate, derived from the underlying pathway (%/year)
>
> — SBTi (2025). Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation, p. 25

**Note:** The SBTi uses a *linear* formula (multiply LARR by years), not a compound formula. For STRIDE implementation, this translates to:

```
E(t) = E(base) × [1 - LARR × (t - base_year)]
```

### Reduction Rates

> "The minimum annual linear reduction rates aligned with 1.5˚C and WB-2˚C are 4.2% and 2.5%, respectively."
>
> — SBTi (2019). Foundations of Science-based Target Setting, Version 1.0, p. 22

| Ambition Level | Annual Rate (LARR) | Cumulative by 2030¹ | Cumulative by 2050² |
|---------------|---------------------|---------------------|---------------------|
| **1.5°C** | 4.2%/year | 21.0% | 105%³ |
| **Well-below 2°C** | 2.5%/year | 12.5% | 62.5% |

¹ Calculation: `LARR × 5` (5 years from 2025→2030)
² Calculation: `LARR × 25` (25 years from 2025→2050)
³ Note: 105% reduction implies net-zero before 2050

**Source for ambition level requirement:**

**Understanding Emission Scopes:**
- **Scope 1**: Direct emissions from sources you own/control (e.g., burning fuel on-site)
- **Scope 2**: Indirect emissions from purchased energy (electricity you buy from the grid) — **this is the depot's primary emission source**
- **Scope 3**: All other indirect emissions in your value chain (suppliers, employee commutes, etc.)

> "C15 – Level of ambition for scope 1 and 2 targets: At a minimum, scope 1 and scope 2 near-term targets shall be consistent with the level of decarbonization required to keep global temperature increase to 1.5°C compared to pre-industrial temperatures."
>
> — SBTi (2025). SBTi Corporate Near-Term Criteria V5.3, p. 12

> "C18 – Level of ambition for scope 3 emissions reductions targets: At a minimum, near-term scope 3 targets (covering total required scope 3 emissions or individual scope 3 categories) shall be aligned with methods consistent with the level of decarbonization required to keep global temperature increase well-below 2°C compared to pre-industrial temperatures."
>
> — SBTi (2025). SBTi Corporate Near-Term Criteria V5.3, p. 12

**Note:** C15/C18 are criteria IDs, not ambition levels. The key difference: Scope 1+2 (direct operations) must meet the stricter 1.5°C target, while Scope 3 (value chain) only needs well-below 2°C — because companies have less control over their supply chain emissions.

### Application to STRIDE Scenarios

Using the linear formula from SBTi with a base of 200,000 kg CO₂:

| Scenario | Ambition | Rate | 2030 Limit | 2050 Limit |
|----------|----------|------|------------|------------|
| Pessimistic | None | 0% | No constraint | No constraint |
| Moderate | WB2C | 2.5%/yr | 175,000 kg | 75,000 kg |
| Optimistic | 1.5°C | 4.2%/yr | 158,000 kg | Net-zero by ~2049 |

**Calculation examples (linear SBTi method):**
- 2030 (Moderate): 200,000 × [1 - 0.025 × 5] = 200,000 × 0.875 = 175,000 kg
- 2030 (Optimistic): 200,000 × [1 - 0.042 × 5] = 200,000 × 0.79 = 158,000 kg

**Base:** 200,000 kg CO₂ (Schmid 50-day simulation baseline, rounded for operational flexibility)

---

## Per-Depot Baseline Calculation

### Methodology

The baseline emissions are calculated from the **first stage run** (2025) assuming grid-only electricity supply:

```
Baseline CO2 = Fleet size × Sim days × Avg daily consumption × Grid CO2 factor
```

### Schmid Depot (50-day simulation)

```
Baseline = 84 vehicles × 50 days × 100 kWh/day × 0.35 kg/kWh
         ≈ 147,000 kg CO2
```

**STRIDE base_limit_kg:** 200,000 kg (rounded up to allow operational flexibility in first stage)

### Metzger Depot (TBD)

- 18 vehicles (4.7× smaller fleet)
- Different utilization pattern
- Requires separate baseline calculation
- Estimated: ~40,000 kg baseline → ~50,000 kg base_limit

---

## Implementation in STRIDE

### Config Structure

```yaml
emissions:
  pathway_type: sbti_aca
  base_year: 2025
  base_limit_kg: 200000
  annual_reduction_rate: 0.042  # 1.5°C scenario (LARR)
```

**Note on formula:** The SBTi uses a linear formula where target ambition = LARR × years (see Equation 4.2, p. 26). This differs from compound decay. For a 25-year horizon with 4.2% LARR, this reaches 105% reduction (i.e., net-zero before 2050).

### Stage-by-Stage Limits (Optimistic, 4.2%/yr)

Using SBTi linear formula: E(t) = E(base) × [1 - LARR × (t - base_year)]

| Stage | Year | Calculation | Limit (kg) |
|-------|------|-------------|------------|
| 1 | 2025 | 200,000 × [1 - 0.042 × 0] | 200,000 |
| 2 | 2030 | 200,000 × [1 - 0.042 × 5] | 158,000 |
| 3 | 2035 | 200,000 × [1 - 0.042 × 10] | 116,000 |
| 4 | 2040 | 200,000 × [1 - 0.042 × 15] | 74,000 |
| 5 | 2045 | 200,000 × [1 - 0.042 × 20] | 32,000 |
| 6 | 2050 | 200,000 × [1 - 0.042 × 25] | 0 (net-zero) |

### Stage-by-Stage Limits (Moderate, 2.5%/yr)

| Stage | Year | Calculation | Limit (kg) |
|-------|------|-------------|------------|
| 1 | 2025 | 200,000 × [1 - 0.025 × 0] | 200,000 |
| 2 | 2030 | 200,000 × [1 - 0.025 × 5] | 175,000 |
| 3 | 2035 | 200,000 × [1 - 0.025 × 10] | 150,000 |
| 4 | 2040 | 200,000 × [1 - 0.025 × 15] | 125,000 |
| 5 | 2045 | 200,000 × [1 - 0.025 × 20] | 100,000 |
| 6 | 2050 | 200,000 × [1 - 0.025 × 25] | 75,000 |

---

## Scenario Definitions

See `configs/scenarios/` for complete scenario configurations.

| Scenario | Grid CO2 Trajectory | CO2 Pathway | Description |
|----------|--------------------|--------------| ------------|
| `pessimistic.yaml` | Constant 0.35 | None | No climate action |
| `moderate.yaml` | BAU (Seckinger) | SBTi WB2C | Current trajectory |
| `optimistic.yaml` | CAP (Seckinger) | SBTi 1.5°C | Aggressive action |

---

## Sources

### SBTi Documents

| File | Description | Citation |
|------|-------------|----------|
| `sources/Documentation-of-target-setting-methods.pdf` | ACA methodology, Equation 4.1 | SBTi (2025). Corporate Net-Zero Standard V2.0 - Target-Setting Methods Documentation. March 2025. |
| `sources/SBTi-criteria.pdf` | Near-term criteria C15, C18 | SBTi (2025). SBTi Corporate Near-Term Criteria V5.3. September 2025. |
| `sources/foundations-of-SBT-setting.pdf` | 4.2%/2.5% LARR derivation | SBTi (2019). Foundations of Science-based Target Setting, Version 1.0. April 2019. |

### Key Quotes Summary

| Claim | Quote | Source |
|-------|-------|--------|
| **4.2% and 2.5% rates** | "The minimum annual linear reduction rates aligned with 1.5˚C and WB-2˚C are 4.2% and 2.5%, respectively." | Foundations, p. 22 |
| **ACA description** | "The ACA produces an absolute emissions pathway between the base year and the target year, representing the company's idealized reduction curve." | Methods Doc, p. 25 |
| **Scope 1+2 ambition** | "At a minimum, scope 1 and scope 2 near-term targets shall be consistent with the level of decarbonization required to keep global temperature increase to 1.5°C" | Criteria, p. 12 (C15) |
| **Scope 3 ambition** | "At a minimum, near-term scope 3 targets...shall be aligned with methods consistent with the level of decarbonization required to keep global temperature increase well-below 2°C" | Criteria, p. 12 (C18) |
| **Grandfathering** | "The method uses a grandfathering allocation principle which implies that the larger a company's emissions in a historic reference year, the larger its share of emissions in a desired target year." | Methods Doc, p. 25 |

### Grid CO2 Factor Projections

| File | Description | URL |
|------|-------------|-----|
| `../grid_co2/sources/energies-14-02527.pdf` | Seckinger & Radgen (2021) | [DOI](https://doi.org/10.3390/en14092527) |

### External References

| Citation | Description |
|----------|-------------|
| SBTi (2025). Corporate Net-Zero Standard V2.0 | Primary methodology reference |
| SBTi (2019). Foundations of Science-based Target Setting | Theoretical background for LARR values |
| Seckinger & Radgen (2021). Energies 14(9):2527 | Grid CO2 factor scenarios |
| GHG Protocol Scope 2 Guidance (2015) | Scope 2 accounting rules |
