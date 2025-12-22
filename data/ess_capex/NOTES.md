# ESS/Battery CAPEX Data

> Last updated: 2025-12-22

---

## 2024 Values for Germany - VERIFIED

**Source:** Fraunhofer ISE, "Stromgestehungskosten Erneuerbare Energien" (LCOE Study), 2024
**File:** `sources/fraunhofer_lcoe_2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/DE2024_ISE_Studie_Stromgestehungskosten_Erneuerbare_Energien.pdf

### From Page 12, Tabelle 1: "Spezifische Anlagenkosten EUR/kW bzw. EUR/kWh bei aktuellen Anlagen in 2024"

| Battery System Type | Investment 2024 niedrig (EUR/kWh) | Investment 2024 hoch (EUR/kWh) |
|---------------------|-----------------------------------|--------------------------------|
| Batteriespeicher für PV-Kleinanlagen (≤30 kWp, 1:1) | 500 | 1000 |
| **Batteriespeicher für PV-Dach-Großanlagen (30 kWp–1 MWp, 2:1)** | **450** | **800** |
| Batteriespeicher für PV-Freiflächenanlagen (>1 MWp, 3:2) | 400 | 600 |

### From Page 21:
> "Für größere PV-Dachanlagen mit Batteriespeicher [...] ergeben sich die Batteriekosten zu **450 bis 800 EUR/kWh**."

> "Für PV-Freiflächenanlagen mit Batteriespeicher [...] wurden Investitionskosten für den Batteriespeicher von **400 bis 600 EUR/kWh** angenommen."

---

## Recommended Value for STRIDE

**For depot-scale (100-500 kWh): 500 €/kWh** (low-mid of "PV-Dach-Großanlagen" range from Tabelle 1)

REVOL-E-TION parameter: `capex_spec` = **0.50 €/Wh**

---

## Projection Trajectory (for multi-stage) - VERIFIED

**Source:** Fraunhofer LCOE Study, Page 30, Tabelle 8: "Annahmen für die Berechnung der Stromgestehungskosten von PV-Batteriesystemen in 2035 und 2045"

### From Tabelle 8 (Batteriespeicherpreis in €/kWh Nutzkapazität, inklusive Installation und ohne MWSt):

| CAPEX [EUR/kWh] | 2024 low | 2024 high | 2035 low | 2035 high | 2045 low | 2045 high |
|-----------------|----------|-----------|----------|-----------|----------|-----------|
| Batteriespeicher für PV-Kleinanlagen (≤30 kWp, 1:1) | 500 | 1000 | 288 | 840 | 180 | 700 |
| Batteriespeicher für PV-Dach-Großanlagen (30 kWp–1 MWp, 2:1) | 450 | 800 | 270 | 675 | 150 | 580 |
| Batteriespeicher für PV-Freiflächenanlagen (>1 MWp, 3:2) | 400 | 600 | 225 | 473 | 130 | 400 |

### Trajectory table (using Großanlagen row):

| Year | €/kWh | Scale vs 2024 | Source |
|------|-------|---------------|--------|
| 2024 | 500 | 1.00 | Page 12, Tabelle 1, low-mid of Großanlagen |
| 2030 | 400 | 0.80 | Interpolated |
| 2035 | 270-675 | 0.54-1.35 | Page 30, Tabelle 8, exact |
| 2040 | 200 | 0.40 | Interpolated |
| 2045 | 150-580 | 0.30-1.16 | Page 30, Tabelle 8, exact |

---

## Notes

- LFP (Lithium Iron Phosphate) is standard for stationary storage
- Costs include installation (inklusive Installation)
- Battery lifetime: 15 years (Page 12: "Die Lebensdauer für Batteriespeicher wurde mit 15 Jahren angesetzt")

---

## Sources

| File | Description |
|------|-------------|
| `sources/fraunhofer_lcoe_2024.pdf` | Primary source for CAPEX values and projections |
