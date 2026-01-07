# STRIDE Command Reference

All commands assume you're in the STRIDE repository root with venv activated:

```bash
cd /Users/arnoclaude/Documents/TUM/Thesis/STRIDE
source venv/bin/activate
```

---

## Base Case Runs

### Test Run (50 simulation days, ~1 hour total)

```bash
# Schmid depot - test
python3 -m multi_stage.main \
    -c configs/schmid_6stage.yaml \
    -s inputs/schmid/scenarios_test_50d.csv \
    -o outputs/base/schmid/test_50d
```

### Production Run (180 simulation days, ~3-4 hours total)

```bash
# Schmid depot - production
python3 -m multi_stage.main \
    -c configs/schmid_6stage.yaml \
    -s inputs/schmid/scenarios_prod_180d.csv \
    -o outputs/base/schmid/prod_180d
```

---

## Sensitivity Analysis Runs

### Individual Sensitivity Cases

```bash
# WACC sensitivity
python3 -m multi_stage.main -c configs/sensitivity/wacc_low.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/wacc_low
python3 -m multi_stage.main -c configs/sensitivity/wacc_high.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/wacc_high

# CO2 factor sensitivity
python3 -m multi_stage.main -c configs/sensitivity/co2_factor_low.yaml -s inputs/schmid/scenarios_co2_low_prod.csv -o outputs/sensitivity/schmid/co2_factor_low
python3 -m multi_stage.main -c configs/sensitivity/co2_factor_high.yaml -s inputs/schmid/scenarios_co2_high_prod.csv -o outputs/sensitivity/schmid/co2_factor_high

# PV CAPEX sensitivity
python3 -m multi_stage.main -c configs/sensitivity/pv_capex_low.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/pv_capex_low
python3 -m multi_stage.main -c configs/sensitivity/pv_capex_high.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/pv_capex_high

# ESS CAPEX sensitivity
python3 -m multi_stage.main -c configs/sensitivity/ess_capex_low.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/ess_capex_low
python3 -m multi_stage.main -c configs/sensitivity/ess_capex_high.yaml -s inputs/schmid/scenarios_prod_180d.csv -o outputs/sensitivity/schmid/ess_capex_high
```

### Batch Run All Sensitivities

```bash
for param in wacc_low wacc_high pv_capex_low pv_capex_high ess_capex_low ess_capex_high; do
    echo "Running sensitivity: $param"
    python3 -m multi_stage.main \
        -c configs/sensitivity/${param}.yaml \
        -s inputs/schmid/scenarios_prod_180d.csv \
        -o outputs/sensitivity/schmid/${param}
done

# CO2 factor uses different scenario files
python3 -m multi_stage.main -c configs/sensitivity/co2_factor_low.yaml -s inputs/schmid/scenarios_co2_low_prod.csv -o outputs/sensitivity/schmid/co2_factor_low
python3 -m multi_stage.main -c configs/sensitivity/co2_factor_high.yaml -s inputs/schmid/scenarios_co2_high_prod.csv -o outputs/sensitivity/schmid/co2_factor_high
```

---

## Single-Stage Comparison (REVOL-E-TION Direct)

```bash
# Naive 2025 baseline - runs REVOL-E-TION directly (not STRIDE)
python -m revoletion.main \
    --settings outputs/single_stage/schmid/settings.csv \
    --scenario outputs/single_stage/schmid/scenarios_single_stage.csv
```

Results saved to `revoletion/results/<timestamp>/`.

---

## Visualization Commands

### Generate Plots for a Single Run

```bash
# PNG only (default)
python3 -m multi_stage.visualize outputs/base/schmid/prod_180d

# PDF only (vector graphics for thesis)
python3 -m multi_stage.visualize outputs/base/schmid/prod_180d --pdf

# Both PNG and PDF
python3 -m multi_stage.visualize outputs/base/schmid/prod_180d --png --pdf

# All formats including LaTeX/TikZ
python3 -m multi_stage.visualize outputs/base/schmid/prod_180d --all

# Custom output directory
python3 -m multi_stage.visualize outputs/base/schmid/prod_180d --plot-dir figures/
```

### Generate Sensitivity Comparison (Tornado Diagram)

```bash
# After running all sensitivity cases:
python3 -m multi_stage.compare_sensitivity \
    outputs/sensitivity/schmid \
    outputs/base/schmid/prod_180d

# Custom output directory
python3 -m multi_stage.compare_sensitivity \
    outputs/sensitivity/schmid \
    outputs/base/schmid/prod_180d \
    -o figures/sensitivity/
```

---

## Available Plots

| Plot | Description |
|------|-------------|
| `investment_timeline.png` | Stacked bar: new investments per stage |
| `cumulative_capacity.png` | Line chart: total PV/ESS capacity over time |
| `cost_breakdown.png` | Bar chart: CAPEX vs NPV per stage |
| `npv_waterfall.png` | Waterfall: cumulative discounted NPV |
| `cost_decline.png` | Line chart: technology cost assumptions |
| `co2_compliance.png` | Bar chart: emissions vs regulatory limits |
| `fleet_growth.png` | Line chart: fleet size evolution |
| `tornado_diagram.png` | Horizontal bar: parameter sensitivity ranking |
| `sensitivity_table.png` | Table: sensitivity metrics summary |

---

## Quick Checks

```bash
# Check venv is active
which python3  # Should show .../STRIDE/venv/bin/python3

# Verify REVOL-E-TION installed
python3 -c "import revoletion; print('OK')"

# List sensitivity configs
ls configs/sensitivity/*.yaml

# Check output structure
find outputs -type d | head -20
```

---

## Thesis Compilation

```bash
cd "/Users/arnoclaude/Documents/TUM/Thesis/LaTeX Master's Thesis"
latexmk -pdf main.tex
```
