# Grid CO2 Emission Factor Data

> Last updated: 2025-12-22

---

## CO2 Scope Justification

**This model counts only grid electricity imports for CO2 emissions.**

### Why this is sufficient:

There is no single source stating "grid electricity = X% of depot emissions." Instead, this is derived from combining:

1. **Grid CO2 factor** (verified): 363 g/kWh (UBA, Page 21)
2. **PV lifecycle emissions** (verified): ~40 g CO2/kWh delivered

**Source:** NREL, "Life Cycle Greenhouse Gas Emissions from Solar Photovoltaics", November 2012
**File:** `sources/nrel_pv_lifecycle_ghg.pdf`
> "Median values for both PV technologies are below **50 g CO2e/kWh**." (Page 2)

3. **ESS lifecycle emissions** (estimate): ~100 kg CO2/kWh capacity over 15-year lifetime

**Source:** MIT Climate Portal, IVL Swedish Energy Agency (not downloaded). Range in literature: 50-150 kg CO2/kWh.

### Calculation for typical depot:

| Component | Assumption | Annual CO2 | Calculation |
|-----------|------------|------------|-------------|
| Grid imports | 1,000 MWh/yr | 363 t | 1,000,000 kWh × 363 g/kWh |
| PV embodied | 200 kWp, 900 kWh/kWp/yr | 7.2 t | 180,000 kWh × 40 g/kWh |
| ESS embodied | 400 kWh capacity | 2.7 t | 400 × 100 kg ÷ 15 years |
| **Total** | | **~373 t** | |
| **Grid share** | | **97%** | 363 ÷ 373 |

**Note:** This calculation uses thesis-specific assumptions. The 90-97% range depends on:
- Grid CO2 factor (higher grid factor → higher grid share)
- PV/ESS sizing relative to consumption
- As grid decarbonizes, embodied share will increase

### Limitation acknowledged:

This model excludes embodied carbon. For a complete lifecycle assessment, add:
- `PV_co2 = 40 g/kWh × annual_pv_generation`
- `ESS_co2 = (100 kg/kWh × capacity) ÷ lifetime_years`

---

## 2024 Values for Germany - VERIFIED

**Primary Source:** Umweltbundesamt (UBA), "Entwicklung der spezifischen Treibhausgas-Emissionen des deutschen Strommix in den Jahren 1990 - 2024", Climate Change 13/2025, March 2025
**File:** `sources/uba_strommix_emissionen_1990_2024.pdf`
**URL:** https://www.umweltbundesamt.de/publikationen/entwicklung-der-spezifischen-treibhausgas-11

### From Page 21, Section 3 "Entwicklung der Emissionsfaktoren des deutschen Strommix":

> "Die durchschnittlichen Kohlendioxidemissionen [...] einer Kilowattstunde Strom (Spezifischer Emissionsfaktor) sinken in den Jahren 1990 bis 2022 von 764 g CO2/kWh auf **433 g CO2/kWh**. [...] Die vorläufigen Ergebnisse für 2023 weisen einen Anstieg auf **386 g CO2/kWh** aus, während für 2024 auf der Grundlage von geschätzten Daten **363 g CO2/kWh** ermittelt werden."

### From Page 29, Section 4 "Zusammenfassung":

> "Die bisherige Entwicklung des in Summe sinkenden Trends von **764 g CO2/kWh im Jahr 1990** (Emissionsfaktor Strommix) auf **433 g CO2/kWh im Jahr 2022** ist positiv zu bewerten. Für 2023 hat das UBA auf der Grundlage vorläufiger Daten „Spezifischen Kohlendioxid-Emissionsfaktor" von **386 g/kWh** errechnet und für 2024 wird ein Wert von **363 g/kWh** geschätzt."

### Summary table from UBA data:

| Year | CO2 Factor (g/kWh) | Status | Source |
|------|-------------------|--------|--------|
| 1990 | 764 | Final | Page 21 |
| 2022 | 433 | Final | Page 21 |
| 2023 | 386 | Preliminary ("vorläufig") | Page 21 |
| 2024 | 363 | Estimated ("geschätzt") | Page 21 |

---

## Recommended Value for STRIDE

**For 2025: 350 g CO2/kWh** (extrapolated from trend)

REVOL-E-TION parameter: `co2_spec_g2s` = **0.00035 kg CO2/Wh**

---

## Projection Trajectory (for multi-stage)

**⚠️ IMPORTANT: Future projections are NOT from verified sources with exact g/kWh values.**

The UBA publication only provides historical data up to 2024. No official German government source provides specific g/kWh emission factor projections for 2030-2050.

### What IS verified (from downloaded sources):

#### 1. Renewables share 2024: 62.7%
**Source:** Fraunhofer ISE, "German Net Power Generation in 2024", Press Release, 03.01.2025
**File:** `sources/fraunhofer_ise_electricity_generation_2024.pdf`, **Page 1**
> "In Germany, net public electricity generation from renewable energy sources reached a record share of **62.7 percent** in 2024."

#### 2. Target: 80% renewables by 2030
**Source:** Clean Energy Wire factsheet
**File:** `sources/cleanenergywire_ghg_targets.html`
> "Germany now aims to bring the renewables share in power consumption to **80 percent by 2030**"

#### 3. Target: 65% GHG reduction by 2030, 88% by 2040, net-zero by 2045
**Source:** Clean Energy Wire factsheet
**File:** `sources/cleanenergywire_ghg_targets.html`
> "neutrality by 2045. It has set interim targets of cutting emissions by at least **65 percent by 2030** and **88 percent by 2040** compared to 1990 levels."

#### 4. Coal phase-out: 2038 (ideally 2030)
**Source:** Clean Energy Wire factsheet
**File:** `sources/cleanenergywire_ghg_targets.html`
> "Germany has passed legislation (in 2020) to end coal-fired power generation by **2038** at the latest [...] The government said 'ideally' it wants to pull forward the coal exit from 2038 to **2030**."

### Estimated emission factors (USE WITH CAUTION):

**⚠️ No source found with exact g/kWh projections for 2030-2045.**

| Year | CO2 Factor (g/kWh) | Source | Confidence |
|------|-------------------|--------|------------|
| 2024 | 363 | UBA Strommix, Page 21, exact quote | ✅ **Verified** |
| 2025 | ~350 | Extrapolated from 2024 trend | ⚠️ Estimate |
| 2030 | 90-200 | No PDF source; derived from 80% renewables target | ❌ **Not verified** |
| 2040 | 20-50 | No PDF source; derived from 88% GHG reduction | ❌ **Not verified** |
| 2045 | ~0-10 | No PDF source; derived from net-zero target | ❌ **Not verified** |

**Calculation basis for 2030 estimate:**
- If 80% renewables (0 g/kWh) + 20% gas (~400 g/kWh) → ~80 g/kWh average
- Range 90-200 accounts for uncertainty in gas share and imports

---

## Supplementary Source

**Source:** Fraunhofer ISE, "German Net Power Generation in 2024: Electricity Mix Cleaner than Ever", Press Release, 03.01.2025
**File:** `sources/fraunhofer_ise_electricity_generation_2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/en/documents/press-releases/2025/0125_ISE_en_PR_electricity_generation2024.pdf

### From Page 2:

> "Due to the increasing share of renewable energies and the decline in coal-fired power generation, electricity generation is lower in CO2 emissions than ever before; since 2014, emissions from electricity generation have **halved (from 312 to approx. 152 million tons of CO2 per year)**. Carbon dioxide emissions from German electricity generation were **58 percent lower than at the start of data collection in 1990**."

This confirms the declining trend in absolute emissions, consistent with the UBA emission factor data.

---

## Notes

- Germany has coal phase-out by 2038 (ideally 2030)
- Imports from neighbors may have different carbon intensity (territorial principle)

---

## Sources

| File | Description |
|------|-------------|
| `sources/uba_strommix_emissionen_1990_2024.pdf` | **Primary** - Emission factors 1990-2024 (verified) |
| `sources/fraunhofer_ise_electricity_generation_2024.pdf` | Absolute CO2 trends, renewables share |
| `sources/agora_energiewende_2024_presentation.pdf` | Sector emissions, no g/kWh projections |
| `sources/dena_leitstudie_summary_en.pdf` | Scenario study, electricity mix but no g/kWh |
| `sources/cleanenergywire_ghg_targets.html` | Policy targets (% reduction, renewables share) |
| `sources/bmwk_electricity_2030.pdf` | BMWK policy paper (no specific g/kWh) |
| `sources/eea_emission_intensity.html` | EU context, no Germany-specific projections |
| `sources/nrel_pv_lifecycle_ghg.pdf` | PV lifecycle emissions (~40 g CO2/kWh) |
| `sources/ukgbc_operational_embodied_carbon.pdf` | Operational vs embodied carbon split |
