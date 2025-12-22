# Grid CO2 Emission Factor Data

> Last updated: 2025-12-22

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

**Note:** UBA does not provide future projections in this publication. The values below are derived from German climate policy targets (coal phase-out 2038, climate neutrality 2045).

| Year | CO2 Factor (g/kWh) | Scale vs 2025 | Source/Notes |
|------|-------------------|---------------|--------------|
| 2025 | 350 | 1.00 | Extrapolated from UBA 2024 trend |
| 2030 | 150 | 0.43 | German Climate Action Plan target |
| 2035 | 80 | 0.23 | Interpolated |
| 2040 | 40 | 0.11 | Near-zero target |
| 2045 | 15 | 0.04 | Approaching net-zero |
| 2050 | 5 | 0.01 | Net-zero electricity sector |

**⚠️ Projection caveat:** The 2030-2050 values are policy targets, not verified projections from UBA. For thesis, cite German Klimaschutzplan or NEP scenarios.

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

- Germany has coal phase-out by 2038
- Imports from neighbors may have different carbon intensity (not counted in German factor per territorial principle)
- Consider hourly variation for detailed charging optimization (Electricity Maps API)

---

## Sources

| File | Description |
|------|-------------|
| `sources/uba_strommix_emissionen_1990_2024.pdf` | Primary source for emission factors |
| `sources/fraunhofer_ise_electricity_generation_2024.pdf` | Supplementary source confirming trends |
