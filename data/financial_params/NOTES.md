# Financial Parameters


---

## Discount Rate / WACC - VERIFIED

**Source:** Fraunhofer ISE, "Levelized Cost of Electricity - Renewable Energy Technologies", June 2024
**File:** `sources/fraunhofer-lcoe-2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/en/documents/publications/studies/EN2024_ISE_Study_Levelized_Cost_of_Electricity_Renewable_Energy_Technologies.pdf

### From Page 15, Table 2: "Input parameter for LCOE calculation"

| PV System Type | WACC nominal | WACC real | Inflation assumed |
|----------------|--------------|-----------|-------------------|
| PV rooftop small (≤30 kWp) | 5.0% | 3.2% | 1.8% |
| **PV rooftop large (>30 kWp)** | **5.3%** | **3.5%** | 1.8% |
| PV utility-scale (>1 MWp) | 5.3% | 3.5% | 1.8% |

### From Page 14-15, Table (Wind/Conventional):

| Technology | WACC nominal | WACC real |
|------------|--------------|-----------|
| Wind onshore | 5.8% | 3.9% |
| Wind offshore | 7.9% | 6.0% |

### Exact quote from Page 15:
> "The real WACC is calculated with an inflation rate of 1.8%"

### Exact quote from Page 14:
> "In this study, the discount rates are determined for each technology based on the market-standard capital costs (weighted average cost of capital - WACC) for the respective investment and are composed proportionally of the interest on debt and return on equity."

---

## Recommended Value for STRIDE

**For depot-scale PV+ESS: WACC real = 3.5%** (from Table 2, PV rooftop large)

If using nominal values: **WACC nominal = 5.3%**

REVOL-E-TION parameter: `wacc` = **0.035** (real) or **0.053** (nominal)

---

## Technology Lifespans - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 15, Table 2

### From Page 15, Table 2:

| Technology | Lifetime (years) | Source |
|------------|------------------|--------|
| **PV systems** | **30** | Table 2, row "Lifetime in years" |
| **Battery storage** | **15** | Table 2, row "Lifetime in years" |

### Exact quote from Page 13:
> "The technical and financial lifespan for PV systems is assumed to be 30 years."

### Exact quote from Page 13:
> "The lifespan of battery storage systems is assumed to be 15 years."

### From Page 14, Table (Wind/Conventional):

| Technology | Lifetime (years) |
|------------|------------------|
| Wind onshore | 25 |
| Wind offshore | 25 |

---

## PV Degradation - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 15, Table 2

### From Page 15, Table 2, row "Annual degradation":
- PV systems: **0.25%** per year

---

## O&M Costs - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 15, Table 2

### From Page 15, Table 2:

| Technology | OPEX fix [EUR/kW] | OPEX var [EUR/kWh] |
|------------|-------------------|-------------------|
| PV rooftop small | 26 | 0 |
| **PV rooftop large** | **21.5** | **0** |
| PV utility-scale | 13.3 | 0 |

### From Page 14, Table (Wind):

| Technology | OPEX fix [EUR/kW] | OPEX var [EUR/kWh] |
|------------|-------------------|-------------------|
| Wind onshore | 32 | 0.007 |
| Wind offshore | 39 | 0.008 |

---

## Sources

| File | Description |
|------|-------------|
| `sources/fraunhofer-lcoe-2024.pdf` | Primary source - Fraunhofer ISE LCOE Study June 2024 |
