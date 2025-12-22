# SMARD Grid Electricity Price Data (G2S)

## Overview

This folder contains wholesale electricity price data from SMARD and the transformation script to convert it into REVOL-E-TION input format with full retail pricing for Bavarian freight forwarding depots.

---

## Data Source

### Wholesale Prices
- **Provider:** Bundesnetzagentur (Federal Network Agency)
- **Platform:** SMARD.de - Strommarktdaten für Deutschland
- **URL:** https://www.smard.de/home/downloadcenter/download-marktdaten/
- **Data Selection:**
  - Oberkategorie: Markt
  - Datenkategorie: Großhandelspreise
  - Marktgebiet: DE/LU (Germany/Luxembourg)
  - Auflösung: Stunde (hourly)
- **Format:** CSV with German formatting (semicolon separator, comma decimal)
- **Data Retrieved:** December 2024 (for 2025 prices)

### Why SMARD
- Official government data source (Bundesnetzagentur)
- Used in prior academic work (Pointner 2025, Biedenbach & Strunz 2024)
- Represents actual day-ahead spot market clearing prices (EPEX Spot)
- Captures hourly volatility essential for charging optimization
- Includes negative prices during renewable oversupply periods

---

## Price Composition

The final G2S electricity price consists of:

```
Total Price = Wholesale (SMARD) + Network Fees + Surcharges + Taxes
```

### 1. Wholesale Component (variable, from SMARD)

| Metric | Value | Source |
|--------|-------|--------|
| 2024 average | ~78 €/MWh | Agora Energiewende Jahresauswertung 2024 |
| 2025 range | -250 to +583 €/MWh | SMARD data (retrieved Dec 2024) |
| Negative hours | ~7% of year | Renewable oversupply periods |

### 2. Network Fees (Bayernwerk Netzentgelte 2025)

**Source:** Bayernwerk Netz GmbH, Preisblatt Netzentgelte Strom 2025
**URL:** https://www.bayernwerk-netz.de/content/dam/revu-global/bayernwerk-netz/files/netz/netzzugang/netzentgeltestrom/bayernwerk-preisblatt-netzentgelte-2025.pdf
**Price Sheet:** LG JLP (Jahresleistungspreis) - Section 1, Page 3

**Selected Category:** Niederspannung, <2,500 Benutzungsstunden
- Typical for freight depots with high peak power but moderate total consumption
- Usage hours = Annual consumption (kWh) / Peak demand (kW)

| Component | Value | Unit |
|-----------|-------|------|
| Arbeitspreis | **7.45** | ct/kWh |
| Leistungspreis | 21.93 | €/kW/a |

**Note:** The Leistungspreis (demand charge) is modeled separately in REVOL-E-TION via the `peakshaving` and `opex_spec_peak` parameters of the GridConnection block.

### 3. Surcharges (Umlagen)

**Source:** netztransparenz.de - Gemeinsame Plattform der deutschen Übertragungsnetzbetreiber
**URLs:**
- KWKG: https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/KWKG/KWKG-Umlage/KWKG-Umlagen-Übersicht/KWKG-Umlage-2025
- Offshore: https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/Offshore-Netzumlage
- §19 StromNEV: https://www.netztransparenz.de/de-de/Erneuerbare-Energien-und-Umlagen/Sonstige-Umlagen/Aufschlag-für-besondere-Netznutzung-§-19-StromNEV-Umlage

**Values valid from 01.01.2025:**

| Surcharge | Value (ct/kWh) | Notes |
|-----------|----------------|-------|
| KWKG-Umlage | 0.277 | CHP promotion |
| Offshore-Netzumlage | 0.816 | Offshore wind grid connection |
| §19 StromNEV (Kategorie A) | 1.558 | For consumption ≤1 GWh/year |
| **Subtotal** | **2.651** | |

**Note on §19 StromNEV categories:**
- Kategorie A (≤1 GWh/a): 1.558 ct/kWh (used here)
- Kategorie B (>1 GWh/a): 0.050 ct/kWh
- Kategorie C (stromkostenintensiv): 0.025 ct/kWh

### 4. Taxes & Fees

| Tax/Fee | Value (ct/kWh) | Source |
|---------|----------------|--------|
| Stromsteuer | 2.05 | StromStG (standard rate) |
| Konzessionsabgabe | 0.11 | KAV (Sondervertragskunde rate) |
| **Subtotal** | **2.16** | |

**Notes:**
- Stromsteuer can be reduced to 0.05 ct/kWh for "produzierendes Gewerbe" upon application
- Konzessionsabgabe varies by municipality; 0.11 ct/kWh is the Sondervertragskunde rate

### 5. Total Retail Markup

| Component | Value (ct/kWh) |
|-----------|----------------|
| Network fees (Arbeitspreis) | 7.45 |
| Surcharges | 2.651 |
| Taxes & fees | 2.16 |
| **Total Markup** | **12.26 ≈ 12** |

**Final formula:**
```
cost (€/Wh) = wholesale (€/MWh) / 1,000,000 + 0.00012
```

---

## Multi-Stage Price Projection (2025-2050)

### Approach

For the multi-stage optimization spanning 2025-2050, we use:
1. **2025 SMARD hourly pattern** as the base (captures daily/weekly/seasonal volatility)
2. **Scaling factors** applied to the wholesale component only
3. **Retail markup held constant** (simplification)

Each stage covers 5 years:
- Stage 1 (2025-2030): Use 2025 data with scale = 1.00
- Stage 2 (2030-2035): Use 2025 pattern with scale = 0.90
- Stage 3 (2035-2040): Use 2025 pattern with scale = 0.85
- Stage 4 (2040-2045): Use 2025 pattern with scale = 0.80
- Stage 5 (2045-2050): Use 2025 pattern with scale = 0.75

### Scaling Factor Justification

| Period | Wholesale Scale | Rationale |
|--------|-----------------|-----------|
| 2025-2030 | 1.00 | Baseline (current SMARD data) |
| 2030-2035 | 0.90 | -10% from accelerated renewables (Agora/Aurora scenarios) |
| 2035-2040 | 0.85 | Continued decline per Energy Brainpool EU Outlook |
| 2040-2045 | 0.80 | Approaching 2050 climate targets |
| 2045-2050 | 0.75 | Full energy transition scenario (NEP/BNetzA) |

**Sources:**
- Agora Energiewende + Aurora Energy Research: "Renewable targets and demand" (2025)
  - URL: https://www.agora-energiewende.de/fileadmin/Projekte/2025/2025-07_DE_EE_2030/Aurora_Apr25_Agora_Renewable_targets_and_demand_Report_as_sent.pdf
- Energy Brainpool: "EU Energy Outlook to 2060"
  - URL: https://energypost.eu/eu-energy-outlook-to-2060-power-prices-and-revenues-predicted-for-wind-solar-gas-hydrogen-more/
- Prognos: Long-term electricity price forecasts for Bavaria
  - URL: https://www.prognos.com/en/project/electricity-price-forecast

### Scaling Formula

```
cost_stage_n (€/Wh) = (wholesale_2025 (€/MWh) × scale_factor / 1,000,000) + 0.00012
```

---

## Negative Prices

### Explanation
SMARD data includes negative wholesale prices, occurring when:
- Renewable generation (wind/solar) exceeds demand
- Inflexible baseload plants cannot ramp down
- Grid operators pay consumers to absorb surplus

### 2025 Data Statistics
- Negative hours: ~573 out of 8,760 (~7%)
- Minimum price: -250.32 €/MWh
- Maximum price: +583.40 €/MWh

### Treatment in Transform
- Negative wholesale prices are **preserved**
- Final cost can be below retail markup (e.g., -250 €/MWh → -0.00013 €/Wh net)
- This correctly models the economic incentive for flexible loads like BET charging

---

## Transformation Process

### Input
- SMARD CSV export with German formatting
- Columns: "Datum von", "Deutschland/Luxemburg [€/MWh] Berechnete Auflösungen"

### Output
- `grid_opex_g2s_YYYY.csv`
- Columns: `time` (ISO format with timezone), `cost` (€/Wh)
- Compatible with REVOL-E-TION GridConnection `opex_spec_g2s` parameter

### Steps
1. Load CSV with German formatting (semicolon separator, comma decimal)
2. Extract DE/LU price column
3. Parse German datetime format (DD.MM.YYYY HH:MM)
4. Convert €/MWh → €/Wh (divide by 1,000,000)
5. Apply scaling factor (for future stages)
6. Add retail markup (0.00012 €/Wh)
7. Format timestamp with CET timezone (+01:00)
8. Export as CSV

### Usage
```bash
# Process 2025 data (scale 1.0)
python transform.py

# Generate scaled data for future stages
python transform.py --scale 0.90  # 2030-2035
python transform.py --scale 0.85  # 2035-2040
python transform.py --scale 0.80  # 2040-2045
python transform.py --scale 0.75  # 2045-2050
```

---

## Files

### Raw
- `Gro_handelspreise_YYYYMMDD_YYYYMMDD_Stunde.csv` - SMARD export

### Processed
- `grid_opex_g2s_2025.csv` - Stage 1 (2025-2030)
- `grid_opex_g2s_2030.csv` - Stage 2 (2030-2035), scaled
- `grid_opex_g2s_2035.csv` - Stage 3 (2035-2040), scaled
- `grid_opex_g2s_2040.csv` - Stage 4 (2040-2045), scaled
- `grid_opex_g2s_2045.csv` - Stage 5 (2045-2050), scaled

---

## Comparison with Prior Work

Franziska Pointner (TUM Bachelor thesis, 2025) used ~31.7 ct/kWh average for G2S.
Our 2025 estimate: ~20 ct/kWh (8 ct wholesale + 12 ct markup).

**Difference explained by:**
1. Her data from Sep 2023 (post-energy crisis, higher wholesale)
2. Different network fee assumptions
3. Possibly different customer category

---

## References

1. Bundesnetzagentur. "SMARD - Strommarktdaten für Deutschland."
   https://www.smard.de/home/downloadcenter/download-marktdaten/

2. Bayernwerk Netz GmbH. "Preisblatt Netzentgelte Strom 2025."
   https://www.bayernwerk-netz.de/content/dam/revu-global/bayernwerk-netz/files/netz/netzzugang/netzentgeltestrom/bayernwerk-preisblatt-netzentgelte-2025.pdf

3. netztransparenz.de. "Gesetzliche Umlagen 2025."
   https://www.netztransparenz.de/

4. Agora Energiewende. "Jahresauswertung 2024." January 2025.
   https://www.agora-energiewende.org/publications

5. Energy Brainpool. "EU Energy Outlook to 2060."
   https://energypost.eu/eu-energy-outlook-to-2060-power-prices-and-revenues-predicted-for-wind-solar-gas-hydrogen-more/

6. Pointner, F. "Energy-Economic Optimization of Freight Forwarding Depots for Electric Trucks." Bachelor Thesis, TUM, 2025.

7. ispex.de. "Umlagen auf Strom 2025."
   https://www.ispex.de/umlagen-auf-strom-2025/

---

## Open Items

- [ ] **Validate with depot electricity bills:** Using Bayernwerk 2025 rates as placeholder until actual depot electricity costs are provided by DT-Cargo or second depot
- [ ] **Refine scaling factors:** Current scaling uses simple linear decline; if time permits, replace with more detailed projections from NEP Szenariorahmen or academic literature
- [ ] **Demand charge modeling:** Verify that REVOL-E-TION `opex_spec_peak` correctly models the Leistungspreis (21.93 €/kW/a) separately from Arbeitspreis
