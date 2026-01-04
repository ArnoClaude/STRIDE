# Charger / EVSE CAPEX


---

## Values for Europe - VERIFIED

**Source:** ACEA & McKinsey, "A European EV Charging Infrastructure Masterplan", 2022
**File:** `sources/acea-ev-charging-masterplan.pdf`
**URL:** https://www.acea.auto/files/Research-Whitepaper-A-European-EV-Charging-Infrastructure-Masterplan.pdf

### From Page 41, Exhibit 27:

| Technology | Cost per kW (€) | Total Charger CAPEX (€) |
|------------|-----------------|-------------------------|
| AC 4-22 kW | 125 | ~1,000 (11 kW) |
| DC 25 kW | 558 | ~14,000 |
| **DC 150 kW** | **400** | **~60,000** |
| **DC 350 kW** | **247** | **~86,000** |
| DC 500+ kW | 208 | ~104,000 |
| DC 1 MW | 260 | ~260,000 |

### Exact quote from Page 40:
> "the 2030 investment per kW ranges from €125 for AC 11 kW to €400 for DC 150 kW. In terms of total investment, while an AC 11 kW charger is expected to cost €1,000 per unit, this is expected to be €104,000 for DC 500+ kW and reach €260,000 for DC 1 MW chargers."

**Note:** Values include hardware, planning/engineering, administration, and installation. Excludes grid investments.

---

## Recommended Value for STRIDE

**For 150 kW DC depot charger: ~60,000 EUR** (400 EUR/kW × 150 kW)
**For 350 kW DC depot charger: ~86,000 EUR** (247 EUR/kW × 350 kW)

REVOL-E-TION parameter: `bev.capex_charger` = **60000** (for 150 kW)

---

## Cost Breakdown (from Exhibit 27)

For DC 150 kW charger (total €60,000):
- Hardware: €51,000 (85%)
- Planning & Engineering: €4,000
- Administration: €1,000
- Installation: €4,000

---

## AC vs DC Charging Strategy

**Source:** NOW GmbH, "Einfach laden am Depot - Leitfaden", 2023
**File:** `sources/now-gmbh-depot-leitfaden.pdf`
**URL:** https://www.now-gmbh.de/wp-content/uploads/2023/11/Einfach-laden-am-Depot_Leitfaden.pdf

For overnight depot charging, 22 kW AC chargers (~€1,500-2,000 installed) may be sufficient for many use cases, reducing CAPEX significantly compared to DC fast charging.

---

## Sources

| File | Description |
|------|-------------|
| `sources/acea-ev-charging-masterplan.pdf` | ACEA/McKinsey European EV Charging Masterplan 2022 |
| `sources/now-gmbh-depot-leitfaden.pdf` | NOW GmbH depot charging guide 2023 |
