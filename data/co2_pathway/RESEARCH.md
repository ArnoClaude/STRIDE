# CO2 Pathway Research for Truck Depot Electrification

> Research date: 2026-01-12
> Context: STRIDE thesis - setting realistic CO2 limits for multi-stage optimization

---

## 1. EU Heavy-Duty Vehicle CO2 Regulation

### Regulation (EU) 2024/1610 (adopted May 2024)

**Fleet-wide CO2 reduction targets for HDV manufacturers (vs 2019-2020 baseline):**

| Year | Reduction Target |
|------|------------------|
| 2025 | -15% |
| 2030 | -45% |
| 2035 | -65% |
| 2040 | -90% |

**Key points:**
- Applies to manufacturers' new vehicle sales (fleet average)
- Urban buses: 100% zero-emission by 2035
- Part of EU Fit for 55 package

**Sources:**
- [Council of EU Press Release](https://www.consilium.europa.eu/en/press/press-releases/2024/05/13/heavy-duty-vehicles-council-signs-off-on-stricter-co2-emission-standards/)
- [ICCT Policy Update](https://theicct.org/wp-content/uploads/2024/05/ID-130-%E2%80%93-EU-CO2_policy_update_final.pdf)
- [EUR-Lex Regulation](https://eur-lex.europa.eu/eli/reg/2024/1610/oj/eng)

---

## 2. How Depots Calculate CO2 Emissions

### Emission Scopes (GHG Protocol)

| Scope | Description | For EV Depot |
|-------|-------------|--------------|
| Scope 1 | Direct emissions (owned vehicles) | Zero for BEVs (no tailpipe) |
| Scope 2 | Purchased electricity | **Main source** - grid charging |
| Scope 3 | Value chain (manufacturing, etc.) | Out of scope for operations |

### Scope 2 Calculation (Well-to-Wheel)

```
Annual CO2 (kg) = Energy consumed (kWh) × Grid emission factor (kg CO2/kWh)
```

**Example for Schmid depot (84 vehicles):**
- Annual mileage: ~50,000 km/vehicle
- Energy consumption: ~1.5 kWh/km (heavy trucks)
- Total annual energy: 84 × 50,000 × 1.5 = 6,300,000 kWh
- With grid factor 0.35 kg/kWh: 2,205,000 kg CO2/year

*Note: Our 50-day simulation represents ~14% of annual operation.*

### Reporting Methods

| Method | Description | Use for STRIDE |
|--------|-------------|----------------|
| Location-based | Uses average grid mix | ✓ Default (conservative) |
| Market-based | Considers PPAs, RECs | Could model as sensitivity |

**Sources:**
- [GHG Protocol Scope 2 Guidance](https://ghgprotocol.org/scope-2-guidance)
- [ISO 14083:2023 Transport GHG Quantification](https://www.iso.org/standard/78864.html)

---

## 3. German Grid CO2 Factor Projections

### Historical and Projected Values

| Year | CO2 Factor (kg/kWh) | Notes |
|------|---------------------|-------|
| 2020 | 0.40 | Pre-coal phase-out |
| 2024 | 0.32 | 60%+ renewables |
| 2025 | 0.32 | Current baseline |
| 2030 | 0.07-0.15 | Coal phase-out complete, 80% renewables |
| 2035 | 0.05-0.08 | continued renewable expansion |
| 2040 | 0.025-0.05 | Near-full renewable |
| 2045 | 0.01-0.03 | Climate neutrality target year |
| 2050 | ~0 | Net-zero electricity |

**Key milestones:**
- Coal phase-out: 2030 (ideally)
- 80% renewable electricity: 2030
- Climate neutrality: 2045 (Germany) / 2050 (EU)

**Sources:**
- [Fraunhofer ISE 2024](https://www.ise.fraunhofer.de/content/dam/ise/en/documents/press-releases/2025/0125_ISE_en_PR_electricity_generation2024.pdf)
- [Nowtricity Germany](https://www.nowtricity.com/country/germany/)
- [FfE Life Cycle Emissions Data](https://opendata.ffe.de/dataset/development-of-life-cycle-based-ghg-emissions-from-the-electricity-mix-broken-down-by-energy-source-germany/)

---

## 4. Science Based Targets (SBTi)

### Land Transport Guidance

**Key requirements:**
- ~4.2% annual reduction for Scope 1+2 (1.5°C pathway)
- Linear pathway to ~90% reduction by 2050
- Scope 3 engagement required for large emitters

**For fleet operators:**
- Set absolute or intensity targets (gCO2/km or gCO2/tkm)
- Must cover all owned/leased vehicles and facilities
- Validated targets require third-party verification

**Sources:**
- [SBTi Land Transport Guidance](https://files.sciencebasedtargets.org/production/files/SBT-transport-guidance-Final.pdf)
- [MIT CTL Transport Guidance](https://ctl.mit.edu/pub/paper/transport-science-based-target-setting-guidance)

---

## 5. Recommended CO2 Pathway for STRIDE

### Option A: Grid Decarbonization Pathway (Recommended)

Base CO2 limit on projected grid emission factors, assuming constant energy demand:

| Year | Grid Factor | Fleet Energy (MWh) | CO2 Limit (kg) | % of 2025 |
|------|-------------|-------------------|----------------|-----------|
| 2025 | 0.35 | 6,300 | 2,205,000 | 100% |
| 2030 | 0.15 | 6,950 | 1,042,500 | 47% |
| 2035 | 0.08 | 7,700 | 616,000 | 28% |
| 2040 | 0.04 | 8,500 | 340,000 | 15% |
| 2045 | 0.02 | 9,400 | 188,000 | 9% |
| 2050 | 0.01 | 10,400 | 104,000 | 5% |

*Scaled to 50-day simulation: divide by ~7.3*

### Option B: SBTi Linear Pathway

4.2% annual reduction from 2025 baseline:
- 2030: -19% (5-year)
- 2040: -34% (15-year) 
- 2050: -65% (25-year)

*Less aggressive than grid projections.*

### Option C: EU HDV Regulation Aligned

Match EU manufacturer targets (-90% by 2040):
- 2025: 100%
- 2030: 55% (-45%)
- 2035: 35% (-65%)
- 2040: 10% (-90%)
- 2050: ~0%

*Most aggressive, may be infeasible.*

---

## 6. Recommendation for STRIDE Configuration

### Current Config (200k → 20k kg)
- 90% reduction over 25 years
- ~8.5% compound annual decline
- **More aggressive than SBTi but plausible with grid decarbonization**

### Proposed Update

Use **Option A (grid decarbonization)** as base case, scaled to 50-day simulation:

| Year | CO2 Limit (kg/50d) | Rationale |
|------|-------------------|-----------|
| 2025 | 300,000 | 2.2M annual ÷ 7.3 |
| 2030 | 140,000 | Grid at 0.15 |
| 2035 | 85,000 | Grid at 0.08 |
| 2040 | 47,000 | Grid at 0.04 |
| 2045 | 26,000 | Grid at 0.02 |
| 2050 | 14,000 | Grid at 0.01 |

**Sensitivity analysis:**
- High CO2: +50% (delayed grid transition)
- Low CO2: -50% (accelerated transition + on-site PV)

---

## 7. Key Takeaways

1. **Depot CO2 is Scope 2** - driven by grid electricity, not vehicle emissions
2. **Grid decarbonization is the main driver** - German grid projected to be near-zero by 2050
3. **90% reduction by 2050 is realistic** - aligns with both grid projections and EU HDV targets
4. **On-site PV accelerates reduction** - STRIDE's investment in PV helps meet tighter limits
5. **Current 200k→20k pathway is reasonable** - conservative interpretation of grid decarbonization

---

## References

1. Council of EU (2024). Heavy-duty vehicles: Council signs off on stricter CO2 emission standards.
2. ICCT (2024). The revised CO2 standards for heavy-duty vehicles in the European Union.
3. Fraunhofer ISE (2025). German Net Power Generation in 2024.
4. GHG Protocol (2015). Scope 2 Guidance.
5. SBTi (2024). Land Transport Science-based Target Setting Guidance.
6. FfE (2024). Development of Life Cycle Based GHG Emissions from the Electricity Mix.
