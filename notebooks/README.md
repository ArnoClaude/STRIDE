# STRIDE Notebooks

This directory contains Jupyter notebooks for validating and demonstrating individual components of the STRIDE framework.

---

## Directory Structure

Each notebook has its own subdirectory containing:
- The notebook file (`.ipynb`)
- An `output/` subdirectory for generated plots, CSVs, and JSON files

```
notebooks/
├── README.md                           # This file
├── 01_test_co2_constraint/            # CO2 constraint validation
│   ├── 01_test_co2_constraint.ipynb
│   └── output/
│       ├── plot_a_investment_vs_co2.png
│       ├── plot_b_economic_impact.png
│       ├── plot_c_abatement_cost_curve.png
│       ├── plot_d_energy_mix.png
│       ├── co2_constraint_results.csv
│       ├── co2_constraint_results.json
│       └── summary_statistics.json
└── 02_future_notebook/                # Future notebooks
    ├── 02_future_notebook.ipynb
    └── output/
```

---

## Output Behavior

**Important:** When you re-run notebook cells that generate plots or export files:
- **Plots ARE overwritten** - `plt.savefig()` replaces existing files without warning
- **CSV/JSON files ARE overwritten** - Previous results are replaced
- **No versioning** - Old outputs are not preserved

**Best Practice:**
- If you want to preserve results from a specific run, manually copy the `output/` directory with a descriptive name (e.g., `output_baseline_run`, `output_2025-11-22`)
- Consider adding timestamps to filenames in the notebook code if you need automatic versioning

---

## Available Notebooks

### 01_test_co2_constraint

**Purpose:** Validates CO2 emission constraint implementation across multiple emission limits.

**Key Features:**
- Tests 7 CO2 scenarios from unlimited to near-zero carbon
- Validates constraint compliance (simulation vs project period)
- Calculates marginal abatement costs
- Generates 4 publication-quality plots

**Outputs:**
- `plot_a_investment_vs_co2.png` - PV/battery scaling and grid import trends
- `plot_b_economic_impact.png` - CAPEX, OPEX, and NPV analysis
- `plot_c_abatement_cost_curve.png` - Cost per kg CO2 avoided
- `plot_d_energy_mix.png` - Energy composition by scenario
- `co2_constraint_results.csv` - Comparison table
- `co2_constraint_results.json` - Full results with metadata
- `summary_statistics.json` - Aggregated statistics

**Run time:** ~60 minutes (7 scenarios × ~8-10 min each)

**Important Note:** The CO2 constraint applies to the **simulation period** (50 days), not the project period (25 years). See notebook for detailed explanation.

---

## Running Notebooks

### Prerequisites

1. **Virtual environment must be activated:**
   ```bash
   source /Users/arnoclaude/Documents/TUM/Thesis/thesis-optimization/venv/bin/activate
   ```

2. **REVOL-E-TION must be installed** (as submodule)

3. **PyCharm/Jupyter must use venv interpreter:**
   - Settings → Project → Python Interpreter
   - Select: `thesis-optimization/venv/bin/python3`

### Running in PyCharm

1. Open notebook in PyCharm
2. Verify interpreter shows "Python 3.9 (venv)" in bottom-right
3. Run cells individually or "Run All"

### Running in Jupyter Lab

```bash
# From STRIDE repo root
cd notebooks/01_test_co2_constraint
jupyter lab 01_test_co2_constraint.ipynb
```

---

## Adding New Notebooks

When creating a new validation notebook:

1. **Create subdirectory:**
   ```bash
   cd notebooks
   mkdir 0X_notebook_name
   cd 0X_notebook_name
   ```

2. **Create notebook** with naming pattern: `0X_notebook_name.ipynb`

3. **Set output path** in notebook setup cell:
   ```python
   NOTEBOOK_OUTPUT = REPO_ROOT / "notebooks" / "0X_notebook_name" / "output"
   NOTEBOOK_OUTPUT.mkdir(exist_ok=True, parents=True)
   ```

4. **Update this README** with notebook description

---

## Notebook Naming Convention

- `01_test_*.ipynb` - Unit tests for individual STRIDE components
- `02_validate_*.ipynb` - Validation studies comparing STRIDE with literature
- `03_case_study_*.ipynb` - Case studies (small/medium/large depot scenarios)
- `04_sensitivity_*.ipynb` - Sensitivity analyses
- `05_results_*.ipynb` - Final thesis results generation

---

## Git Tracking

**Tracked:**
- ✅ Notebook files (`.ipynb`)
- ✅ This README

**Not tracked (in `.gitignore`):**
- ❌ `output/` directories (generated files, can be large)
- ❌ Checkpoint files (`.ipynb_checkpoints/`)

If you want to commit specific results for reproducibility, remove them from `.gitignore` temporarily.

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'revoletion'"

**Solution:** Jupyter is using system Python, not venv
- Configure PyCharm interpreter to use venv (see "Running Notebooks" above)
- Verify with: `import sys; print(sys.executable)` should show path ending in `venv/bin/python3`

### Problem: "REVOL-E-TION return code: 1"

**Solution:** Check that venv is activated and REVOL-E-TION is installed
```bash
source venv/bin/activate
cd revoletion
pip install -e .
```

### Problem: Old plots still showing in notebook

**Solution:** Clear output and re-run
- Jupyter: Kernel → Restart & Clear Output → Run All
- PyCharm: Right-click notebook → Clear All Outputs

---

## Future Notebooks (Planned)

- `02_test_scenario_builder.ipynb` - Technology cost decline validation
- `03_test_sequential_optimizer.ipynb` - Multi-stage optimization logic
- `04_case_study_small_depot.ipynb` - 5-truck depot (baseline)
- `05_case_study_medium_depot.ipynb` - 20-truck depot
- `06_case_study_large_depot.ipynb` - 50-truck depot
- `07_sensitivity_analysis.ipynb` - Parameter sensitivity study

---

*Last updated: November 2025*
