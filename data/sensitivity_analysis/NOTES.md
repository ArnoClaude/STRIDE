# Sensitivity Analysis Documentation

---

## Methodology

### Approach: One-Way Sensitivity Analysis (OWSA) + Tornado Diagram

This thesis uses **One-Way Sensitivity Analysis (OWSA)** where each parameter is varied independently while holding all others at their base case values. Results are visualized using a **tornado diagram** to rank parameters by their impact on the objective function (NPV).

**Justification for OWSA:**
- Standard approach for Master's theses in energy systems optimization
- Provides clear interpretation of individual parameter impacts
- Sufficient for identifying most influential parameters
- More sophisticated methods (Monte Carlo, multi-way) are optional extensions

### Combined Scenarios (Optional Extension)

In addition to OWSA, two combined scenarios test correlated parameter changes:

| Scenario | Description | Parameters |
|----------|-------------|------------|
| **Pessimistic** | Unfavorable economic conditions | High WACC + High CO2 factor + High technology costs |
| **Optimistic** | Favorable conditions | Low WACC + Low CO2 factor + Low technology costs |

---

## Sensitivity Parameters

### Selection Criteria

Parameters were selected for sensitivity analysis based on:
1. **Uncertainty**: Parameters with significant estimation uncertainty
2. **Impact**: Parameters expected to significantly affect NPV or investment decisions
3. **Policy relevance**: Parameters subject to policy changes or market dynamics
4. **Data availability**: Parameters with documented ranges in literature

### Parameters Included

| Parameter | Low | Base | High | Unit | Rationale |
|-----------|-----|------|------|------|-----------|
| WACC | 2.5% | 3.5% | 5.7% | % | Financing conditions uncertainty |
| CO2 emission factor | 0.25 | 0.35 | 0.45 | kg/kWh | Grid decarbonization uncertainty |
| PV CAPEX | 900 | 1000 | 1600 | €/kWp | Technology cost uncertainty |
| ESS CAPEX | 450 | 500 | 800 | €/kWh | Technology cost uncertainty |

### Parameters Excluded (with justification)

| Parameter | Reason for exclusion |
|-----------|---------------------|
| Grid electricity price | Already varies hourly in model; trajectory scaling is secondary effect |
| Charger CAPEX | Smaller cost share; less impact on NPV than PV/ESS |
| Grid connection CAPEX | One-time cost; low sensitivity expected |
| Fleet size | Treated as exogenous input from depot operator |
| Technology decline rates | Correlated with CAPEX; would double-count uncertainty |

---

## Parameter Bounds: Sources and Justification

### 1. WACC (Weighted Average Cost of Capital)

**Base value:** 3.5% (real)
**Low value:** 2.5% (real)
**High value:** 5.7% (nominal)

**Source:** Fraunhofer ISE, "Levelized Cost of Electricity - Renewable Energy Technologies", June 2024
**File:** `../financial_params/sources/fraunhofer-lcoe-2024.pdf`

**Page 13, Table 2:** "Input parameter for LCOE calculation"

| PV System Type | WACC nominal | WACC real |
|----------------|--------------|-----------|
| PV rooftop small (≤30 kWp) | 5.0% | 3.2% |
| **PV rooftop large (>30 kWp)** | **5.3%** | **3.5%** |

**Justification for bounds:**
- **Low (2.5%)**: Favorable financing conditions (low-risk corporate borrower, green bonds)
- **Base (3.5%)**: Fraunhofer real WACC for large PV rooftop systems
- **High (5.7%)**: Fraunhofer nominal WACC (includes inflation), represents higher-risk financing

---

### 2. CO2 Emission Factor

**Base value:** 0.35 kg/kWh (350 g/kWh)
**Low value:** 0.25 kg/kWh (250 g/kWh)
**High value:** 0.45 kg/kWh (450 g/kWh)

**Source for base value:** Umweltbundesamt (UBA), "Entwicklung der spezifischen Treibhausgas-Emissionen des deutschen Strommix", Climate Change 13/2025
**File:** `../grid_co2/sources/uba_strommix_emissionen_1990_2024.pdf`

**Page 21:**
> "Die vorläufigen Ergebnisse für 2023 weisen einen Anstieg auf 386 g CO2/kWh aus, während für 2024 auf der Grundlage von geschätzten Daten **363 g CO2/kWh** ermittelt werden."

**Justification for bounds:**
- **Low (0.25 kg/kWh)**: Optimistic grid decarbonization scenario (~30% below 2024 level). Consistent with accelerated coal phase-out by 2030 and 80%+ renewables.
- **Base (0.35 kg/kWh)**: Slightly below 2024 actual (363 g/kWh), representing continued improvement.
- **High (0.45 kg/kWh)**: Conservative scenario (~25% above base). Accounts for slower renewable deployment or increased gas generation.

**Note:** ±30% sensitivity range is standard practice for emission factor uncertainty. See:
- Wietschel et al. (2019), Fraunhofer ISI: load management only affects emissions by 4-6 percentage points
- Noussan & Neirotti (2020): year-to-year variation ~18% for any given country

---

### 3. PV CAPEX

**Base value:** 1000 €/kWp
**Low value:** 900 €/kWp
**High value:** 1600 €/kWp

**Source:** Fraunhofer ISE, "Stromgestehungskosten Erneuerbare Energien" (LCOE Study), 2024
**File:** `../pv_capex/sources/fraunhofer_lcoe_2024.pdf`

**Page 12, Tabelle 1:** "Spezifische Anlagenkosten EUR/kW bzw. EUR/kWh bei aktuellen Anlagen in 2024"

| PV System Type | Investment 2024 niedrig (EUR/kWp) | Investment 2024 hoch (EUR/kWp) |
|----------------|-----------------------------------|--------------------------------|
| PV Dach Kleinanlagen (≤30 kWp) | 1000 | 2000 |
| **PV Dach Großanlagen (>30 kWp)** | **900** | **1600** |
| PV Freifläche (>1 MWp) | 700 | 900 |

**Justification for bounds:**
- **Low (900 €/kWp)**: Fraunhofer "niedrig" value for large rooftop PV. Represents favorable procurement, economies of scale.
- **Base (1000 €/kWp)**: Low-mid of Fraunhofer range. Conservative estimate for depot-scale systems.
- **High (1600 €/kWp)**: Fraunhofer "hoch" value. Represents higher-cost installations (complex roof structures, older buildings, premium components).

---

### 4. ESS CAPEX

**Base value:** 500 €/kWh
**Low value:** 450 €/kWh
**High value:** 800 €/kWh

**Source:** Fraunhofer ISE, "Stromgestehungskosten Erneuerbare Energien" (LCOE Study), 2024
**File:** `../ess_capex/sources/fraunhofer_lcoe_2024.pdf`

**Page 12, Tabelle 1:** "Spezifische Anlagenkosten EUR/kW bzw. EUR/kWh bei aktuellen Anlagen in 2024"

| Battery System Type | Investment 2024 niedrig (EUR/kWh) | Investment 2024 hoch (EUR/kWh) |
|---------------------|-----------------------------------|--------------------------------|
| Batteriespeicher für PV-Kleinanlagen (≤30 kWp, 1:1) | 500 | 1000 |
| **Batteriespeicher für PV-Dach-Großanlagen (30 kWp–1 MWp, 2:1)** | **450** | **800** |
| Batteriespeicher für PV-Freiflächenanlagen (>1 MWp, 3:2) | 400 | 600 |

**Page 19:**
> "Für größere PV-Dachanlagen mit Batteriespeicher [...] ergeben sich die Batteriekosten zu **450 bis 800 EUR/kWh**."

**Justification for bounds:**
- **Low (450 €/kWh)**: Fraunhofer "niedrig" value for large rooftop systems. Competitive LFP battery pricing.
- **Base (500 €/kWh)**: Low-mid of range, consistent with current market for 100-500 kWh systems.
- **High (800 €/kWh)**: Fraunhofer "hoch" value. Represents premium systems, smaller scale, or supply chain constraints.

---

## Output Structure

Each sensitivity run produces the same outputs as the base case:

```
outputs/sensitivity/{depot}/{parameter}_{direction}/
├── stages/                    # Per-stage scenario CSVs
│   ├── scenario_2025.csv
│   ├── scenario_2030.csv
│   └── ...
├── plots/                     # Generated visualizations
│   ├── investment_timeline.png
│   ├── npv_waterfall.png
│   ├── co2_compliance.png
│   └── ...
├── investment_timeline.csv    # Summary of investments per stage
└── multi_stage_results.json   # Full results for analysis
```

---

## Analysis Plan

### 1. Run Sensitivity Cases

```bash
# Example: Run all Schmid sensitivities
cd /Users/arnoclaude/Documents/TUM/Thesis/STRIDE
source venv/bin/activate

for param in wacc_low wacc_high co2_factor_low co2_factor_high pv_capex_low pv_capex_high ess_capex_low ess_capex_high; do
    python3 -m multi_stage.main \
        -c configs/sensitivity/${param}.yaml \
        -s inputs/schmid/scenarios_${param}.csv \
        -o outputs/sensitivity/schmid/${param}
done
```

### 2. Generate Tornado Diagram

Compare NPV across all sensitivity cases to identify most influential parameters:

| Parameter | Low NPV | Base NPV | High NPV | Swing (High-Low) |
|-----------|---------|----------|----------|------------------|
| WACC | [TBD] | [TBD] | [TBD] | [TBD] |
| CO2 factor | [TBD] | [TBD] | [TBD] | [TBD] |
| PV CAPEX | [TBD] | [TBD] | [TBD] | [TBD] |
| ESS CAPEX | [TBD] | [TBD] | [TBD] | [TBD] |

### 3. Interpret Results

Key questions to answer:
1. Which parameter has the largest impact on NPV?
2. Do any parameters change the optimal investment sequence?
3. At what parameter values does the CO2 constraint become non-binding?
4. How robust are PV/ESS sizing decisions to parameter uncertainty?

---

## References

### Primary Sources

| Citation | File | Description |
|----------|------|-------------|
| Fraunhofer ISE (2024a) | `../financial_params/sources/fraunhofer-lcoe-2024.pdf` | LCOE study, WACC values (English) |
| Fraunhofer ISE (2024b) | `../pv_capex/sources/fraunhofer_lcoe_2024.pdf` | LCOE study, PV/ESS CAPEX (German) |
| UBA (2025) | `../grid_co2/sources/uba_strommix_emissionen_1990_2024.pdf` | German grid emission factors |
| Wietschel et al. (2019) | `../grid_co2/sources/WP02-2019_Treibhausgasemissionsbilanz_von_Fahrzeugen.pdf` | BEV emissions, load management impact |
| Noussan & Neirotti (2020) | `../grid_co2/sources/energies-13-02527.pdf` | Hourly vs annual CO2 variation |

