# Grid Connection CAPEX (Baukostenzuschuss)


---

## 2025 Values for Germany - VERIFIED

**Source:** ÜZ Mainfranken eG, "Preisblatt Baukostenzuschuss (Strom)", Gültigkeit ab 01.08.2025
**File:** `sources/uez-bkz-2025.pdf`
**URL:** https://www.uez.de/_Resources/Persistent/8/2/0/5/8205f6ef741e1925087a7324717d4b9890ba4606/Preisblatt%20Baukostenzuschuss%20Strom%2C%20g%C3%BCltig%20ab%2001.08.2025.pdf

### From Page 1:

| Netzebene | Calculation | BKZ (EUR/kW) |
|-----------|-------------|--------------|
| NE4 (Umspannung HS/MS) | 124.00 × 0.79 | **98.75** |
| **NE5 (Mittelspannung)** | 152.25 × 0.65 | **98.96** |
| NE6 (Umspannung MS/NS) | 169.80 × 0.62 | **105.28** |
| NE7 (Niederspannung) | - | **121.00** |

### Exact quote (Page 1, Section 2):
> "Für 2025 ergibt sich ein BKZ in der Netzebene 5 von 152,25 EUR/kW * 0,65 = 98,96 EUR/kW."

---

## Recommended Value for STRIDE

**Medium voltage grid connection (Netzebene 5): 98.96 EUR/kW**

REVOL-E-TION parameter: `grid.capex_spec` = **0.09896 EUR/W**

---

## Notes

- BKZ = Baukostenzuschuss (construction cost subsidy)
- One-time fee paid to utility for upstream grid reinforcement
- Based on contracted capacity (kW), not energy consumption
- Does not include customer's own installation costs (transformer, cabling within property)
- Values are net; add 19% VAT for gross prices
- For EV charging (steuerbare Verbrauchseinrichtungen): 20% reduction per BNetzA BK8-22/010-A

---

## Sources

| File | Description |
|------|-------------|
| `sources/uez-bkz-2025.pdf` | ÜZ Mainfranken official price sheet, valid from 01.08.2025 |
