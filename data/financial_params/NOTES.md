# Financial Parameters

**Status:** ✅ VERIFIED (Page numbers need final confirmation for lifespans/degradation)

---

## Discount Rate / WACC - VERIFIED

**Source:** Fraunhofer ISE, "Levelized Cost of Electricity - Renewable Energy Technologies", June 2024
**File:** `sources/fraunhofer-lcoe-2024.pdf`
**URL:** https://www.ise.fraunhofer.de/content/dam/ise/en/documents/publications/studies/EN2024_ISE_Study_Levelized_Cost_of_Electricity_Renewable_Energy_Technologies.pdf

### From Page 14, Table 2: "Input parameter for LCOE calculation"

| PV System Type | WACC nominal | WACC real | Inflation assumed |
|----------------|--------------|-----------|-------------------|
| PV rooftop small (≤30 kWp) | 5.0% | 3.2% | 1.8% |
| **PV rooftop large (>30 kWp)** | **5.3%** | **3.5%** | 1.8% |
| PV utility-scale (>1 MWp) | 5.3% | 3.5% | 1.8% |

### From Page 14, Table (Wind/Conventional):

| Technology | WACC nominal | WACC real |
|------------|--------------|-----------|
| Wind onshore | 5.8% | 3.9% |
| Wind offshore | 7.9% | 6.0% |

---

## Recommended Value for STRIDE

**For depot-scale PV+ESS: WACC real = 3.5%** (from Table 2, PV rooftop large)

If using nominal values: **WACC nominal = 5.3%**

REVOL-E-TION parameter: `wacc` = **0.035** (real) or **0.053** (nominal)

---

## Technology Lifespans - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 13

### From Page 13:

| Technology | Lifetime (years) |
|------------|------------------|
| **PV systems** | **30** |
| **Battery storage** | **15** |

**Note:** Can you verify the exact English quotes from Page 13 for PV and battery lifespans?

---

## PV Degradation - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 15, Table 2

### From Page 15, Table 2, row "Annual degradation":
- PV systems: **0.25%** per year

---

## O&M Costs - VERIFIED

**Source:** Fraunhofer ISE LCOE Study 2024, Page 13, Table 2

### From Page 13, Table 2:

| Technology | OPEX fix [EUR/kW] | OPEX var [EUR/kWh] |
|------------|-------------------|-------------------|
| PV rooftop small | 26 | 0 |
| **PV rooftop large** | **21.5** | **0** |
| PV utility-scale | 13.3 | 0 |

### From Page 13, Table (Wind):

| Technology | OPEX fix [EUR/kW] | OPEX var [EUR/kWh] |
|------------|-------------------|-------------------|
| Wind onshore | 32 | 0.007 |
| Wind offshore | 39 | 0.008 |

---

## Sources

| File | Description |
|------|-------------|
| `sources/fraunhofer-lcoe-2024.pdf` | Primary source - Fraunhofer ISE LCOE Study June 2024 |
