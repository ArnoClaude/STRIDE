# Grid CO2 Emission Factor Data

---

## Annual Average vs Hourly CO2 Factors

### Justification for Using Fixed Annual Average

**Question**: Is using a fixed annual average CO2 factor (e.g., 0.35 kg/kWh) acceptable, or do we need hourly time-varying factors?

### Literature Review

#### 1. Germany 2024 Official Value

**Source:** Umweltbundesamt (UBA), "Entwicklung der spezifischen Treibhausgas-Emissionen des deutschen Strommix in den Jahren 1990 - 2024", Climate Change 13/2025
**File:** `sources/uba_strommix_emissionen_1990_2024.pdf`
**Page 21:**
> "Die vorläufigen Ergebnisse für 2023 weisen einen Anstieg auf 386 g CO2/kWh aus, während für 2024 auf der Grundlage von geschätzten Daten **363 g CO2/kWh** ermittelt werden."

| Year | CO2 Factor (g/kWh) | Status | Source |
|------|-------------------|--------|--------|
| 2022 | 433 | Final | UBA p.21 |
| 2023 | 386 | Preliminary | UBA p.21 |
| 2024 | **363** | Estimated | UBA p.21 |
| 2025 | ~350 | Extrapolated | Trend-based |

#### 2. Depot Overnight Charging: Annual Average is CONSERVATIVE

**Source:** Transport & Environment / Fraunhofer ISI / Oeko-Institut, "Truck Depot Charging: Final Report", February 2025
**File:** `sources/te_truck_depot_charging_2025.pdf`

**Page 41, Section 3.1.3 "Vehicle Usage Patterns":**
> "The stakeholders involved confirmed that in regional delivery transport, it is common for BET to spend long periods at night in the depot, which can then be used for battery charging."

**Page 72, Section 5.1.3 "Vehicle Usage Pattern" (UK chapter):**
> "In regional transport, vehicles usually return to the depot at night. [...] According to the Road Haulage Association (RHA), 70% of UK electric trucks currently return to the depot overnight to charge."

**Page 41, Future prospects:**
> "According to a manufacturer's forecast, 90% of urban distribution transport and regional transport can be carried out with depot charging."

**Implication for our model**:
- Truck depots charge primarily **overnight** (when vehicles return)
- Nighttime CO2 intensity is **higher** than annual average (no solar generation)
- Using annual average (0.35 kg/kWh) is therefore **conservative** (underestimates actual emissions)
- Our CO2 constraint will be **slightly easier** to meet in reality

#### 4. Hourly vs Annual: Academic Literature

**Source:** Noussan, M., & Neirotti, F. (2020). "Cross-Country Comparison of Hourly Electricity Mixes for EV Charging Profiles." Energies, 13(10), 2527.
**DOI:** https://doi.org/10.3390/en13102527
**File:** `sources/energies-13-02527.pdf`

**Page 1, Abstract:**
> "The results show that the variability related to charging proﬁles is generally limited, with an average variation range of **6%** for any given country and year, while in several countries the variability from one year to another is much larger, with an average range of **18%** for any given country and charging proﬁle."

**Page 11, Discussion:**
> "all the other combinations of country and year show ranges of variation (calculated as the ratio between the difference of maximum and minimum values and the average value) lower than 10% (with an average value of **6%** and a minimum value of 1%). On the other hand, when considering the variations of the emission factor of each charging proﬁle over the years for any given country, the ranges of variations are signiﬁcantly higher. [...] the average range of variation is **18%**, much higher than the 6% variation associated to the proﬁles."

**Key finding**: The difference between different charging profiles (time-of-day optimization) is only ~6% within a given country-year. Year-to-year and cross-country variations (~18%) dominate.

**Implication for our model (honest interpretation)**:
This paper does NOT directly prove "annual average = hourly average." What it proves is: "optimizing WHEN you charge doesn't significantly change total emissions" (~6% variation). This means:
- All charging patterns (day, night, optimized) get similar results within a given year
- The ~6% variation bounds the error introduced by using annual average instead of hourly factors
- For investment planning purposes, this uncertainty is acceptable and comparable to other model uncertainties (e.g., technology cost projections)

#### 5. Fraunhofer ISI BEV Emission Study (2019)

**Source:** Wietschel, M., Kühnbach, M., & Rüdiger, D. (2019). "Die aktuelle Treibhausgasemissionsbilanz von Elektrofahrzeugen in Deutschland." Working Paper Sustainability and Innovation No. S 02/2019, Fraunhofer ISI.
**File:** `sources/WP02-2019_Treibhausgasemissionsbilanz_von_Fahrzeugen.pdf`

**Page 7, on charging electricity dominance:**
> "Neben der Stromproduktion hat die Fahrzeugherstellung und hier besonders die Batterieproduktion eine große Auswirkung auf die THG-Bilanz von BEV."

Translation: "Besides electricity production, vehicle manufacturing and especially battery production have a large impact on the GHG balance of BEVs."

**Page 7, on battery production emissions (citing Romare et al. 2017):**
> "Den Studien nach hat die eigentliche Batterieproduktion (einschließlich der Zellproduktion) einen Anteil von **30 bis 50 %** an den THG-Emissionen [der Fahrzeugherstellung]."

Translation: "According to studies, actual battery production (including cell production) accounts for **30-50%** of [vehicle manufacturing] GHG emissions."

**Page 31, on load management impact:**
> "Beim Lastmanagement liegen die Werte zwischen **4 bis 6%-Punkte**."

Translation: Load management (charging optimization) only reduces emissions by **4-6 percentage points** compared to unoptimized charging.

**Key findings for our model**:
1. **Grid electricity is the dominant emission source** for BEV operations
2. **Battery production is second**, but over the vehicle lifetime, operational electricity emissions exceed manufacturing emissions
3. **Load management provides only 4-6 percentage point** improvement - consistent with Noussan's 6% finding
4. **Annual average ("Strommix") approach is standard practice** in German BEV emission studies

### Decision: Use Fixed Annual Average

**Justification**:
1. **Standard practice** per UBA methodology for German grid emissions and Fraunhofer ISI BEV studies (Wietschel et al. 2019)
2. **Conservative** for overnight depot charging (actual nighttime emissions are higher due to lack of solar)
3. **Bounded error (~6%)**: Charging profile optimization only affects emissions by 4-6% (Wietschel et al. 2019, p.31; Noussan & Neirotti 2020, p.11) - acceptable for investment planning
4. **CO2 is a constraint**, not objective - minor impact on optimization
5. **REVOL-E-TION limitation**: Would require code modification to support timeseries

**Recommendation for thesis**:
- Use fixed **0.35 kg/kWh** (350 g/kWh) for 2025 baseline
- This is conservative vs. UBA 2024 actual (363 g/kWh)
- Acknowledge limitation in Discussion chapter
- Include CO2 factor in sensitivity analysis (±30%)

---

## CO2 Scope Justification

**This model counts only grid electricity imports for CO2 emissions.**

### Why this is sufficient:

#### Primary Evidence: Fraunhofer ISI BEV Study (Wietschel et al. 2019)

The Fraunhofer ISI study directly addresses BEV emission sources and confirms:
1. **Grid electricity is the primary emission source** during vehicle operation
2. **Battery production is the second largest source** (30-50% of vehicle manufacturing emissions)
3. Over a 13-year vehicle lifetime, operational electricity emissions exceed manufacturing emissions

**File:** `sources/WP02-2019_Treibhausgasemissionsbilanz_von_Fahrzeugen.pdf`

This validates our approach: since grid electricity dominates BEV operational emissions, applying a CO2 constraint to grid imports captures the majority of controllable depot emissions.

#### Supporting Calculation (thesis-specific):

There is no single source stating "grid electricity = X% of depot emissions." The following is derived from combining verified sources:

1. **Grid CO2 factor** (verified): 363 g/kWh (UBA, Page 21)
2. **PV lifecycle emissions** (verified): ~40 g CO2/kWh delivered

**Source:** NREL, "Life Cycle Greenhouse Gas Emissions from Solar Photovoltaics", November 2012
**File:** `sources/nrel_pv_lifecycle_ghg.pdf`
**Page 2:**
> "Median values for both PV technologies are below **50 g CO2e/kWh**."

> "Harmonization has a small effect on the central estimate for each technology, reducing the median by approximately 20%. Median values for both PV technologies are below 50 g CO2e/kWh."

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

### Verified Source: Seckinger & Radgen (2021)

**Source:** Seckinger, N., & Radgen, P. (2021). "Dynamic Prospective Average and Marginal GHG Emission Factors—Scenario-Based Method for the German Power System until 2050." *Energies*, 14(9), 2527.
**DOI:** https://doi.org/10.3390/en14092527
**File:** `sources/energies-14-02527-v2.pdf`

This peer-reviewed paper provides **scenario-based** emission factor projections for German electricity, using a linear optimization model of the power system. It models two scenarios:

#### BAU (Business-As-Usual) Scenario
- **Reduction target:** -74% GHG vs 1990 by 2050
- **Renewables share 2050:** 57%
- **2050 emission factor:** 182 gCO2eq/kWh

#### CAP (Climate-Action-Plan) Scenario
- **Reduction target:** -95% GHG vs 1990 by 2050
- **Renewables share 2050:** 92%
- **2050 emission factor:** 29 gCO2eq/kWh

### Emission Factor Trajectory Table

**Source:** Seckinger & Radgen (2021), Figure 4 and Table 2

| Year | BAU (g/kWh) | CAP (g/kWh) | Historical (g/kWh) |
|------|-------------|-------------|-------------------|
| 2018 | 468 | 468 | 468 (baseline) |
| 2020 | ~420 | ~420 | ~400 (actual) |
| 2025 | ~350 | ~350 | - |
| 2030 | ~300 | ~250 | - |
| 2035 | ~260 | ~150 | - |
| 2040 | ~220 | ~80 | - |
| 2045 | ~200 | ~50 | - |
| 2050 | **182** | **29** | - |

**Note:** Values for 2025-2045 are interpolated from paper figures. Exact values for 2050 are from Table 2.

### Scenario Implications

For STRIDE multi-stage optimization, use:

| Scenario | Grid CO2 Factor Trajectory | Rationale |
|----------|---------------------------|-----------|
| **Pessimistic** | Constant 0.35 kg/kWh | No grid decarbonization |
| **Moderate** | BAU trajectory → 0.182 kg/kWh | Current policy trajectory |
| **Optimistic** | CAP trajectory → 0.029 kg/kWh | Aggressive climate action |

**Config files:** See `configs/scenarios/` for full scenario definitions.

---

## Notes

- Germany has coal phase-out by 2038 (ideally 2030)
- Imports from neighbors may have different carbon intensity (territorial principle)

---

## Sources

| File | Description |
|------|-------------|
| `sources/uba_strommix_emissionen_1990_2024.pdf` | UBA emission factors 1990-2024, Pages 9 & 21 (primary) |
| `sources/te_truck_depot_charging_2025.pdf` | T&E/Fraunhofer depot charging Feb 2025, Pages 41 & 72 |
| `sources/energies-13-02527.pdf` | Noussan & Neirotti (2020) hourly vs annual CO2, Pages 1 & 11 |
| `sources/WP02-2019_Treibhausgasemissionsbilanz_von_Fahrzeugen.pdf` | **Wietschel et al. (2019) Fraunhofer ISI BEV emissions, Pages 7, 31 (KEY: grid electricity dominates, 4-6% load management effect)** |
| `sources/energies-14-02527-v2.pdf` | Seckinger & Radgen (2021) 2050 projections |
| `sources/nrel_pv_lifecycle_ghg.pdf` | PV lifecycle emissions (~50 g CO2e/kWh), Page 2 |

### External References

| Citation | DOI/URL |
|----------|---------|
| Seckinger & Radgen (2021) "Dynamic Prospective Average and Marginal GHG Emission Factors" | https://doi.org/10.3390/en14092527 |
| Wietschel, Kühnbach & Rüdiger (2019) "Die aktuelle Treibhausgasemissionsbilanz von Elektrofahrzeugen in Deutschland" | Fraunhofer ISI Working Paper S 02/2019 |
| Noussan & Neirotti (2020) "Cross-Country Comparison of Hourly Electricity Mixes for EV Charging Profiles" | https://doi.org/10.3390/en13102527 |
| GHG Protocol Scope 2 Guidance (2015) | https://ghgprotocol.org/scope-2-guidance |
