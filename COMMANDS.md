# STRIDE Command Reference

All commands assume you're in the STRIDE repository root with venv activated:

```bash
cd /Users/arnoclaude/Documents/TUM/Thesis/STRIDE
source venv/bin/activate
```

---

## New Run System (Recommended)

Runs are now self-contained in `runs/<name>/` with full traceability.

### Basic Usage

```bash
# Auto-generated run name (recommended)
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv

# Explicit run name
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv \
    --name my_custom_run_name

# With run type (for organization)
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv \
    --type base
```

### Run Types

- `base` - Standard optimization runs (default)
- `sensitivity` - Parameter sensitivity analysis
- `test` - Quick test runs
- `debug` - Debugging runs

---

## Base Case Runs

### Test Run (50 simulation days, ~1 hour total)

```bash
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv \
    --type base
```

### Production Run (180 simulation days, ~3-4 hours total)

```bash
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type base
```

---

## Sensitivity Analysis Runs

```bash
# WACC sensitivity
python3 -m multi_stage.main \
    -c configs/sensitivity/wacc_low.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type sensitivity

python3 -m multi_stage.main \
    -c configs/sensitivity/wacc_high.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type sensitivity

# PV CAPEX sensitivity
python3 -m multi_stage.main \
    -c configs/sensitivity/pv_capex_low.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type sensitivity

# ESS CAPEX sensitivity
python3 -m multi_stage.main \
    -c configs/sensitivity/ess_capex_low.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type sensitivity

# CO2 factor sensitivity (uses different scenario files)
python3 -m multi_stage.main \
    -c configs/sensitivity/co2_factor_low.yaml \
    -s inputs/schmid/scenarios/co2_low_prod.csv \
    --type sensitivity
```

---

## Single-Stage Comparison (REVOL-E-TION Direct)

```bash
# Naive 2025 baseline - runs REVOL-E-TION directly (not STRIDE)
python -m revoletion.main \
    --settings inputs/schmid/settings.csv \
    --scenario inputs/schmid/scenarios/test_50d.csv
```

---

## Visualization Commands

### Generate Plots for a Run

```bash
# PNG only (default)
python3 -m multi_stage.visualize runs/2026-01-07_base_schmid_test_50d

# PDF only (vector graphics for thesis)
python3 -m multi_stage.visualize runs/2026-01-07_base_schmid_test_50d --pdf

# Both PNG and PDF
python3 -m multi_stage.visualize runs/2026-01-07_base_schmid_test_50d --png --pdf
```

### Generate Sensitivity Comparison

```bash
# Compare all sensitivity runs against base
python3 -m multi_stage.compare_sensitivity \
    runs/ \
    runs/2026-01-07_base_schmid_prod_180d
```

---

## Run Output Structure

Each run creates a self-contained directory:

```
runs/2026-01-07_base_schmid_test_50d/
├── manifest.yaml              # Full traceability (inputs, git, params)
├── config.yaml                # Copy of config used
├── scenario_template.csv      # Copy of input scenario
├── settings.csv               # Generated settings for REVOL-E-TION
├── stages/                    # Generated per-stage scenarios
├── revoletion/                # REVOL-E-TION outputs (contained)
├── multi_stage_results.json   # Aggregated results
├── investment_timeline.csv
└── plots/
```

---

## Quick Checks

```bash
# Check venv is active
which python3  # Should show .../STRIDE/venv/bin/python3

# Verify REVOL-E-TION installed
python3 -c "import revoletion; print('OK')"

# List recent runs
ls -lt runs/ | head -10

# View a run's manifest
cat runs/<run_name>/manifest.yaml

# Check input structure
ls inputs/schmid/
ls inputs/schmid/scenarios/
ls inputs/schmid/timeseries/
```

---

## Directory Structure

```
STRIDE/
├── configs/
│   ├── base/                  # Base case configs
│   │   └── schmid_6stage.yaml
│   ├── sensitivity/           # Sensitivity analysis configs
│   │   ├── wacc_low.yaml
│   │   └── ...
│   └── default.yaml           # Default values
├── inputs/
│   └── schmid/
│       ├── settings.csv       # REVOL-E-TION settings
│       ├── scenarios/         # Scenario templates
│       │   ├── test_50d.csv
│       │   └── prod_180d.csv
│       └── timeseries/        # Time-varying data
│           ├── bev_log_*.csv
│           ├── dem_timeseries_*.csv
│           └── grid_opex_*.csv
├── runs/                      # All run outputs (self-contained)
│   └── <run_name>/
└── outputs/                   # Legacy outputs (deprecated)
```

---

## Thesis Compilation

```bash
cd "/Users/arnoclaude/Documents/TUM/Thesis/LaTeX Master's Thesis"
latexmk -pdf main.tex
```
