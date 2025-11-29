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

## Standard Notebook Structure

All validation notebooks should follow this structure for consistency:

### Title Cell (Markdown)
```markdown
# [Feature Name] Implementation & Validation

[One-sentence description]

## Objectives
1. [Primary objective]
2. [Secondary objective]
3. [Validation objective]
```

### Section 1: Motivation & Context
- **Why** this feature/test is needed (2-3 paragraphs max)
- Problem statement and REVOLETION limitations
- Connection to STRIDE thesis goals
- Keep concise, avoid verbosity

### Section 2: Implementation (if applicable)
- Document code changes with snippets
- File locations and line numbers
- Key technical points (3-5 bullets max)
- Summary table of files modified
- **Avoid**: Implementation details, bug fix stories, verbose explanations

### Section 3: Validation/Testing
- Setup & imports
- Path definitions
- Run optimization/test
- Load and extract results
- Comparison tables
- Validation checks with explicit pass/fail status

### Section 4: Visualizations or Summary
- Custom plots (if applicable)
- Export summary statistics to JSON/CSV
- **Avoid**: IFrame embeds (use static plots instead)

### Section 5: Key Findings (Final Section)
- Validation status (✅ PASS or ⚠️ FAIL)
- Main takeaways (3-5 concise bullets)
- Implications for multi-stage optimization
- **Avoid**: "Next Steps" sections, future work, thesis implications beyond scope

---

## Style Guidelines

### Writing Style
- **Concise**: Sacrifice grammar for brevity where appropriate
- **Natural language**: Avoid AI-sounding prose, overly formal tone
- **Active voice**: "Added constraint" not "Constraint was added"
- **No emojis**: Unless explicitly requested
- **No metadata**: Author, date, project name in title cell

### Code Cells
- One logical operation per cell
- Clear variable names (`co2_limit_kg` not `x`)
- Comments only where logic isn't self-evident
- Type conversions explicit: `float(value)` for CSV data
- Progress indicators: `✓ Loaded data`, `✓ Saved to: path`

### Validation Checks
Always include explicit pass/fail validation:
```python
✓ PASS | bev_mg_1: 3,372.7 kg ≤ 100,000 kg (slack: 96,627.3 kg)
✗ FAIL | bev_mg_2: 1,500.0 kg > 1,000 kg (violation: 500.0 kg)
```

### Data Handling Conventions
- Convert CSV strings to numeric immediately: `float(df['value'])`
- Handle None/NaN explicitly
- Consistent units (document in code):
  - Power: W internally, display as kW (`/1000`)
  - Energy: Wh internally, display as kWh (`/1000`)
  - Costs: USD, display as kUSD (`/1000`)
  - Emissions: kg CO2

### Output File Naming
- Descriptive names: `comparison_table.csv` not `table.csv`
- Numbered plots: `plot_1_investment_scaling.png`
- Lowercase with underscores: `summary_statistics.json`

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

**Purpose:** Validates CO2 emission constraint implementation across 4 emission limits.

**Key Features:**
- Tests 4 CO2 scenarios: 100t, 10t, 1t, 0.1t limits
- Validates constraint compliance with explicit pass/fail checks
- Shows investment scaling response to tightening CO2 limits
- Demonstrates correct grid import calculation (derived from CO2)

**Outputs:**
- `comparison_table.csv` - Scenario comparison across all metrics
- `summary.json` - Aggregated statistics and metadata

**Structure:**
1. Motivation & Context (concise, 2 paragraphs)
2. Implementation - Code Changes (3 files modified)
3. Validation with 4 Scenarios (7 subsections)
4. Summary Statistics

**Run time:** ~5 minutes (4 scenarios in single REVOLETION call)

**Important Notes:**
- CO2 constraint applies to **simulation period** (50 days), not project (25 years)
- Grid imports calculated from CO2: `grid_import_kwh = co2_actual_kg / 0.4`
- IFrame dispatch plots removed (404 errors, not essential for validation)

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

## Common Pitfalls to Avoid

Based on lessons learned from notebook development:

### Content Issues
- ❌ Including author/date/project metadata in title
- ❌ Mentioning bug fixes or implementation war stories
- ❌ Adding "Next Steps" or future work sections
- ❌ Using overly verbose, AI-sounding language
- ❌ Over-explaining obvious code or results

### Technical Issues
- ❌ Using IFrame embeds for plots (404 errors, path issues)
- ❌ Extracting wrong metrics from CSV (e.g., net vs gross grid imports)
- ❌ Forgetting to convert CSV string values to numeric types
- ❌ Not validating constraint compliance with explicit checks
- ❌ Inconsistent units between display and calculation

### Structure Issues
- ❌ Too many sections or subsections (keep to 4-5 main sections)
- ❌ Mixing validation logic with visualization code
- ❌ Not preparing data variables before using them in plots
- ❌ Missing clear section separators (`---`)

### Best Practices
- ✅ Derive grid imports from CO2 when direct measurement unavailable
- ✅ Add progress indicators (`✓ Saved to: path`)
- ✅ Show explicit pass/fail validation with tolerances
- ✅ Export summary statistics to JSON for reproducibility
- ✅ Use concise, natural language throughout

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

## Quick Reference

**For future chats working on notebooks:**
1. Read this README first
2. Follow "Standard Notebook Structure" section
3. Use "Style Guidelines" for consistency
4. Check "Common Pitfalls to Avoid" before committing
5. Update this README when adding new notebooks

---

*Last updated: November 29, 2025*
