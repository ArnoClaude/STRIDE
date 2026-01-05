# Peak Demand Charges (Leistungspreis)


---

## German Network Tariff Structure

German industrial electricity network tariffs consist of two components:

| Component | German Term | Unit | Basis |
|-----------|-------------|------|-------|
| **Energy charge** | Arbeitspreis | ct/kWh | Total energy consumed |
| **Capacity charge** | Leistungspreis | EUR/kW/year | Peak power demand |

The **Arbeitspreis** is proportional to total energy consumption. The **Leistungspreis** is based on the customer's highest 15-minute average power demand during the billing period, reflecting the grid capacity reserved for that customer.

---

## Annual Utilization (Benutzungsstunden)

The unit **h/a** (hours per year) represents annual utilization hours, calculated as:

```
Utilization (h/a) = Annual energy consumption (kWh) ÷ Peak demand (kW)
```

This metric indicates how consistently a customer uses their peak capacity:
- **Low h/a** (<2,500): Peaky load profile, capacity used intermittently
- **High h/a** (≥2,500): Flat load profile, capacity used consistently
- **Maximum possible**: 8,760 h/a (continuous operation at peak)

---

## Two-Tier Tariff Structure

German network operators offer two tariff structures optimized for different load profiles:

| Parameter | <2,500 h/a | ≥2,500 h/a |
|-----------|------------|------------|
| **Load profile** | Peaky, intermittent | Flat, consistent |
| **Leistungspreis** | Low (16.53 EUR/kW/a) | High (191.79 EUR/kW/a) |
| **Arbeitspreis** | High (~8.59 ct/kWh) | Low (~1.58 ct/kWh) |

The tariffs are designed such that total annual costs are approximately equal at the 2,500 h/a threshold. Customers select their tariff structure at contract time based on expected utilization.

---

## Peak Demand Measurement

The Leistungspreis is determined by the **single highest 15-minute average power demand** during the billing period (typically one year). This measurement approach:

- Uses 15-minute averaging (not instantaneous peaks)
- Takes the maximum value across all 15-minute intervals in the year
- Applies this single peak value to calculate the annual capacity charge

**Annual capacity charge calculation:**
```
Leistungspreis_annual = Peak_demand (kW) × Leistungspreis (EUR/kW/a)
```

---

## 2025 Values for Germany - VERIFIED

**Source:** Netze ODR GmbH, "Vorläufige Preisblätter für die Nutzung des Stromverteilnetzes", Gültig ab 01.01.2025
**File:** `sources/netze-odr-2025-preliminary.pdf`
**URL:** https://www.netze-odr.de/fileadmin/Netze-ODR/Dokumente/Unternehmen/Veroeffentlichungen/Netzentgelte/Netzentgelte_Strom_2025_vorlaeufig.pdf

### From Page 2, Preisblatt 1:

| Netzebene | Leistungspreis <2500 h/a | Leistungspreis ≥2500 h/a | Arbeitspreis ≥2500 h/a |
|-----------|--------------------------|--------------------------|------------------------|
| Umspannung zur Mittelspannung | 16.42 EUR/kW/a | 192.77 EUR/kW/a | 1.47 ct/kWh |
| **Mittelspannungsnetz** | **16.53 EUR/kW/a** | **191.79 EUR/kW/a** | **1.58 ct/kWh** |
| Umspannung zur Niederspannung | 21.42 EUR/kW/a | 174.93 EUR/kW/a | 2.27 ct/kWh |
| Niederspannungsnetz | 10.83 EUR/kW/a | 149.46 EUR/kW/a | 1.38 ct/kWh |

---

## Recommended Value for STRIDE

**For depot with high utilization (≥2500 h/a):**
- Medium voltage (Mittelspannung): **191.79 EUR/kW/year**

**For depot with low utilization (<2500 h/a):**
- Medium voltage: **16.53 EUR/kW/year**

REVOL-E-TION parameter: `grid.opex_spec_peak` = **0.19179 EUR/W/year** (high utilization)

### Note on Current STRIDE Configuration

The current STRIDE scenarios use **16.53 EUR/kW/year** (the <2,500 h/a category). This is correct for overnight depot charging, which typically exhibits peaky load profiles:
- Charging concentrated in ~8-12 hours overnight
- For a depot with ~1 MW peak and ~1,500 MWh annual consumption: utilization = 1,500 h/a → <2,500 h/a category

The low utilization tariff (high Arbeitspreis, low Leistungspreis) is appropriate because overnight depot charging has high peak-to-average ratios.

---

## Implications for Depot Charging

Electric truck depots with DC fast charging typically exhibit:
- **High instantaneous power demand** (multiple vehicles charging simultaneously)
- **Moderate total energy consumption** (vehicles absent during operating hours)
- **Low utilization** (<2,500 h/a) due to peaky charging patterns

This load profile creates a strong economic incentive for **peak shaving** through:

1. **Stationary battery storage (ESS)**: Buffer grid demand during charging peaks
2. **Smart charging**: Stagger vehicle charging to reduce simultaneous demand
3. **PV integration**: Reduce grid draw during daylight hours

**Example impact:**
For a depot with 500 kW peak demand reduced to 300 kW through peak shaving:
- Annual savings: (500 - 300) kW × 191.79 EUR/kW = **38,358 EUR/year**

---

## Sources

| File | Description |
|------|-------------|
| `sources/netze-odr-2025-preliminary.pdf` | Netze ODR preliminary network tariffs 2025 |
| `sources/bundesnetzagentur-monitoring-2024.pdf` | BNetzA monitoring report (overview) |
