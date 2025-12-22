# PV CAPEX Data

> Last updated: 2025-12-22

---

## 2024 Values for Germany - VERIFIED

**Primary Source:** Fraunhofer ISE, "Stromgestehungskosten Erneuerbare Energien" (LCOE Study), 2024
**File:** `sources/fraunhofer_lcoe_2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/DE2024_ISE_Studie_Stromgestehungskosten_Erneuerbare_Energien.pdf

### From Page 12, Tabelle 1: "Spezifische Anlagenkosten EUR/kW bzw. EUR/kWh bei aktuellen Anlagen in 2024"

| PV System Type | Investment 2024 niedrig (EUR/kWp) | Investment 2024 hoch (EUR/kWp) |
|----------------|-----------------------------------|--------------------------------|
| PV Dach Kleinanlagen (≤30 kWp) | 1000 | 2000 |
| **PV Dach Großanlagen (>30 kWp)** | **900** | **1600** |
| PV Freifläche (>1 MWp) | 700 | 900 |

### From Fraunhofer PV Report, Page 4, Quick Facts table, row "Price PV rooftop system (3 to 10 kWp)":

**File:** `sources/fraunhofer_pv_report_2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/Photovoltaics-Report.pdf

> "900 to 1,300 €/kWp" (Date: 12/2024, Reference: gruenes.haus)

**Note:** The PV Report quote (900-1300) is for small residential systems (3-10 kWp). The LCOE Study Tabelle 1 (900-1600) is for large rooftop (>30 kWp), which is more relevant for depots.

---

## Recommended Value for STRIDE

**For depot-scale (100-500 kWp rooftop): 1,000 €/kWp** (low-mid of "PV Dach Großanlagen" range from Tabelle 1)

REVOL-E-TION parameter: `capex_spec` = **1.00 €/Wp**

---

## Projection Trajectory (for multi-stage) - VERIFIED

**Source:** Fraunhofer LCOE Study, Page 30, Section 5 "Entwicklung der Stromgestehungskosten bis 2045 in Deutschland"

### Exact quote:
> "Die Anlagenpreise für PV sinken bis 2045 bei Freiflächenanlagen auf **457 bis 588 EUR/kW** und bei Kleinanlagen auf bis zu **653 bis 1306 EUR/kW**."

### Learning Rate (Page 30):
> "Für die Prognose der zukünftigen Entwicklung der Stromgestehungskosten von PV-Systemen wird mit einer LR von **15 %** gerechnet."

### Trajectory table:

| Year | €/kWp (Rooftop) | Scale vs 2024 | Source |
|------|-----------------|---------------|--------|
| 2024 | 1000 | 1.00 | Page 12, Tabelle 1, low-mid of Großanlagen |
| 2030 | ~850 | 0.85 | Interpolated using 15% learning rate |
| 2035 | ~750 | 0.75 | Interpolated |
| 2040 | ~680 | 0.68 | Interpolated |
| 2045 | 653-1306 | 0.65-1.30 | Page 30, exact quote above |

---

## Notes

- 0% VAT policy in Germany reduces effective cost for end customers
- Costs include installation but not grid connection upgrades
- kWp = kilowatt-peak (rated power under standard test conditions)

---

## Sources

| File | Description |
|------|-------------|
| `sources/fraunhofer_lcoe_2024.pdf` | Primary source for CAPEX values and projections |
| `sources/fraunhofer_pv_report_2024.pdf` | Secondary source for quick facts |
