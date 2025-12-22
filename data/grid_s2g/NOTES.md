# Grid Feed-in Price Data (S2G)

## Overview

This folder contains feed-in revenue data for electricity sold from the depot to the grid (Site-to-Grid). For PV systems >100 kWp, German law (EEG) requires direct marketing, compensated at the monthly solar market value (Marktwert Solar).

---

## Data Source

### Monatsmarktwerte Solar
- **Provider:** netztransparenz.de (Platform of German TSOs)
- **URL:** https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/EEG/Transparenzanforderungen/Marktprämie/Marktwertübersicht
- **Data:** Monthly average market values for solar electricity (Marktwert Solar)
- **Unit:** ct/kWh
- **Update Frequency:** Monthly, published by 10th of following month

### Why Marktwert Solar
- Required compensation method for PV systems >100 kWp under EEG 2023
- Represents actual average revenue from direct marketing
- Technology-specific (solar has different profile than wind)
- Published by transmission system operators (official source)

---

## 2025 Data (Jan-Nov)

| Month | Marktwert Solar (ct/kWh) |
|-------|--------------------------|
| Jan | 11.511 |
| Feb | 11.099 |
| Mar | 5.027 |
| Apr | 3.041 |
| May | 1.997 |
| Jun | 1.843 |
| Jul | 5.923 |
| Aug | 3.832 |
| Sep | 4.307 |
| Oct | 6.980 |
| Nov | 9.102 |
| Dec | (not yet available) |

**Average (Jan-Nov):** ~5.9 ct/kWh

**Note:** Solar market value is typically lower than spot price because solar generation peaks at midday when prices are often depressed due to high renewable supply.

---

## Comparison with Prior Work

Franziska Pointner used a constant -7.4 ct/kWh for S2G (September 2023 value).

Our 2025 data shows significant monthly variation:
- Winter months (Jan-Feb, Nov): ~9-11 ct/kWh (higher demand, less solar)
- Summer months (May-Jun): ~2 ct/kWh (solar oversupply depresses prices)

Using monthly values is more accurate than a constant.

---

## Transformation Process

### Input
- netztransparenz.de Monatsmarktwerte CSV
- Row: "MW Solar" (monthly solar market values)

### Output
- `grid_opex_s2g_YYYY.csv`
- Columns: `time` (ISO format with timezone), `cost` (€/Wh, **negative** = revenue)
- Hourly resolution (monthly value repeated for all hours in that month)

### Conversion
```
cost (€/Wh) = -1 × marktwert (ct/kWh) / 100,000
```

The negative sign indicates this is **revenue** for the site (REVOL-E-TION convention).

### Usage
```bash
# Process 2025 data
python transform.py

# Generate scaled data for future stages
python transform.py --year 2030 --scale 0.90
python transform.py --year 2035 --scale 0.85
python transform.py --year 2040 --scale 0.80
python transform.py --year 2045 --scale 0.75
```

---

## Multi-Stage Projection

For future stages, we apply the same scaling factors as G2S wholesale prices:

| Stage | Period | Scale | Rationale |
|-------|--------|-------|-----------|
| 1 | 2025-2030 | 1.00 | Baseline |
| 2 | 2030-2035 | 0.90 | More renewables → lower market values |
| 3 | 2035-2040 | 0.85 | Continued trend |
| 4 | 2040-2045 | 0.80 | Approaching saturation |
| 5 | 2045-2050 | 0.75 | Full transition |

**Note:** Solar market values may decline faster than wholesale prices as solar penetration increases (cannibalization effect). This is a simplification.

---

## Files

### Raw
- `monatsmarktwerte_2025.csv` - netztransparenz.de export

### Processed
- `grid_opex_s2g_2025.csv` - Stage 1 (2025-2030)
- `grid_opex_s2g_2030.csv` - Stage 2 (scaled)
- `grid_opex_s2g_2035.csv` - Stage 3 (scaled)
- `grid_opex_s2g_2040.csv` - Stage 4 (scaled)
- `grid_opex_s2g_2045.csv` - Stage 5 (scaled)

---

## References

1. netztransparenz.de. "Marktwertübersicht."
   https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/EEG/Transparenzanforderungen/Marktprämie/Marktwertübersicht

2. Bundesministerium der Justiz. "EEG 2023 - Erneuerbare-Energien-Gesetz."
   https://www.gesetze-im-internet.de/eeg_2014/

3. Pointner, F. "Energy-Economic Optimization of Freight Forwarding Depots for Electric Trucks." Bachelor Thesis, TUM, 2025.

---

## Open Items

- [ ] **December 2025 data:** Not yet available (will be published ~Jan 10, 2026). Currently using average of available months.
- [ ] **Cannibalization effect:** Consider if solar market values should decline faster than wholesale in future stages.
- [ ] **Direct marketing fees:** Actual revenue is Marktwert minus ~0.2-0.4 ct/kWh for direct marketer fees. Not modeled here.
