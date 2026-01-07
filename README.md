# STRIDE

**Sequential Temporal Resource Investment for Depot Electrification**

Master's Thesis Project - Technical University of Munich (TUM)
Author: Arno Claude
Duration: October 2025 - April 2026

---

## Overview

STRIDE is a multi-stage optimization framework for electric truck depot infrastructure planning. It extends the [REVOL-E-TION](https://github.com/tum-ens/revol-e-tion) model to optimize sequential investment decisions across multiple time horizons (2025-2055) for:

- **PV solar panels** (renewable energy generation)
- **Battery energy storage systems** (ESS)
- **EV chargers** (depot charging infrastructure)
- **Grid connections** (import/export capacity)

Unlike traditional single-stage optimization, STRIDE implements a **myopic sequential approach** that better reflects real-world investment decisions under uncertainty, where future technology costs and demand patterns are not perfectly known.

---

## Key Features

- **Multi-stage planning**: Optimizes investments across 5-year intervals (2025, 2030, 2035, 2040, 2045, 2050)
- **Technology cost decline**: Incorporates projected cost reductions for PV, batteries, and chargers
- **CO2 emission constraints**: Optional carbon budget limits for decarbonization scenarios
- **Financial metrics**: NPV, CAPEX, OPEX, LCOE calculations over 25-year project lifetime
- **Extensible architecture**: Built on REVOL-E-TION's Pyomo/oemof-solph MILP framework

---

## Installation

### Prerequisites

- **Python 3.9+** (tested with Python 3.9.6)
- **Virtual environment** (strongly recommended)

### Setup

1. **Clone the repository with submodules:**
   ```bash
   git clone --recurse-submodules https://github.com/your-username/STRIDE.git
   cd STRIDE
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install REVOL-E-TION submodule:**
   ```bash
   cd revoletion
   pip install -e .
   cd ..
   ```

5. **Verify installation:**
   ```bash
   python -c "import revoletion; print('REVOL-E-TION installed successfully')"
   ```

### Important: Virtual Environment

**⚠️ All code must be run within the virtual environment.** The project dependencies (including Pyomo, oemof-solph, and REVOL-E-TION) are isolated to the venv to avoid conflicts with system packages.

If using **PyCharm/Jupyter**, configure the project interpreter to use `venv/bin/python3`:
- PyCharm: Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter → Select `venv/bin/python3`
- Jupyter: Ensure kernel uses venv Python (check with `import sys; print(sys.executable)`)

---

## Development Status

- ✅ REVOL-E-TION integration and understanding
- ✅ CO2 constraint implementation and validation
- ✅ Multi-stage optimizer development
- ✅ Visualization module
- 🚧 Case studies and sensitivity analysis (CURRENT)
- 📅 Thesis writing

---

## Usage

### Running Multi-Stage Optimization

```bash
# Activate virtual environment
source venv/bin/activate

# Run 6-stage optimization (auto-generated run name)
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv

# Run with explicit name and type
python3 -m multi_stage.main \
    -c configs/base/schmid_6stage.yaml \
    -s inputs/schmid/scenarios/test_50d.csv \
    --name my_test_run \
    --type base

# Sensitivity analysis
python3 -m multi_stage.main \
    -c configs/sensitivity/wacc_low.yaml \
    -s inputs/schmid/scenarios/prod_180d.csv \
    --type sensitivity
```

Each run creates a self-contained directory in `runs/<name>/` with:
- `manifest.yaml` - Full traceability (inputs, git commit, parameters)
- `config.yaml` - Copy of config used
- `scenario_template.csv` - Copy of input scenario
- `revoletion/` - REVOL-E-TION outputs (contained)
- `multi_stage_results.json` - Aggregated results

### Generating Visualizations

```bash
# Generate PNG + PDF plots (default)
python3 -m multi_stage.visualize runs/2026-01-07_base_schmid_test_50d

# Generate only PNG
python3 -m multi_stage.visualize runs/<run_name> --png

# Generate only PDF (vector graphics for thesis)
python3 -m multi_stage.visualize runs/<run_name> --pdf

# Generate all formats
python3 -m multi_stage.visualize runs/<run_name> --all
```

**Available plots:**
- `investment_timeline` - Stacked bar chart of new investments per stage
- `cumulative_capacity` - Line chart of total PV/ESS capacity over time
- `cost_breakdown` - CAPEX vs NPV per stage
- `npv_waterfall` - Cumulative discounted NPV
- `cost_decline` - Technology cost assumptions
- `co2_compliance` - Emissions vs regulatory limits
- `fleet_growth` - Fleet size evolution

### Architecture Diagram

A full-page TikZ diagram showing data flow between STRIDE and REVOL-E-TION is available:

```bash
# Compile with LaTeX
cd multi_stage
pdflatex architecture_diagram.tex
```

This diagram shows:
- **Blue boxes**: STRIDE wrapper code (new)
- **Green boxes**: REVOL-E-TION existing code
- **Orange hatched boxes**: Modifications to REVOL-E-TION (CO2 constraint, size_existing extensions)
- **Arrows**: Control flow and data flow between components
- **Loop**: Stage iteration with capacity carry-forward

---

## Folder Structure

```
STRIDE/
├── configs/                    # YAML configuration files for multi-stage runs
│   ├── base/                  # Base case configurations
│   │   └── schmid_6stage.yaml # Main 6-stage config (2025-2050)
│   ├── sensitivity/           # Sensitivity analysis configs
│   │   ├── wacc_low.yaml
│   │   └── ...
│   └── default.yaml           # Default parameter values
├── data/                       # Research data and source documents
│   ├── grid_co2/              # CO2 emission factors + sources
│   ├── pv_capex/              # PV cost projections + sources
│   ├── ess_capex/             # Battery cost projections + sources
│   ├── financial_params/      # WACC, discount rates + sources
│   ├── depot_Schmid/          # Case study data (Schmid depot)
│   └── .../                   # Other data categories
├── inputs/                     # Scenario input files for REVOL-E-TION
│   └── schmid/                # Schmid depot scenario
│       ├── settings.csv       # REVOL-E-TION settings
│       ├── scenarios/         # Scenario templates
│       │   ├── test_50d.csv   # 50-day test scenario
│       │   └── prod_180d.csv  # 180-day production scenario
│       └── timeseries/        # Time-varying data
│           ├── bev_log_*.csv  # Vehicle charging logs
│           ├── dem_*.csv      # Fixed demand profiles
│           └── grid_opex_*.csv # Electricity prices
├── runs/                       # All run outputs (self-contained)
│   └── <run_name>/            # Each run is fully traceable
│       ├── manifest.yaml      # Traceability: inputs, git, params
│       ├── config.yaml        # Copy of config used
│       ├── scenario_template.csv
│       ├── settings.csv       # Run-specific settings
│       ├── stages/            # Generated per-stage scenarios
│       ├── revoletion/        # REVOL-E-TION outputs (contained)
│       └── plots/
├── multi_stage/               # STRIDE multi-stage wrapper code
│   ├── main.py               # CLI entry point
│   ├── sequential_optimizer.py
│   ├── scenario_builder.py
│   ├── results_parser.py
│   ├── manifest.py           # Run traceability
│   ├── visualize.py          # Thesis-quality plotting
│   └── config_loader.py
├── revoletion/                # REVOL-E-TION submodule (modified)
│   ├── revoletion/           # Core optimization code
│   │   ├── blocks.py         # Energy system components
│   │   ├── constraints.py    # CO2 constraint (added)
│   │   └── simulation.py     # Main simulation loop
│   └── example/              # Reference examples
├── outputs/                   # Legacy outputs (deprecated, use runs/)
└── notebooks/                 # Development/testing notebooks
```

---

## Contributing

This is a thesis project and is not currently accepting external contributions. For questions or collaboration inquiries, please contact the author.

---

## License

This project uses REVOL-E-TION as a submodule, which is licensed under [its own terms](https://github.com/tum-ens/revol-e-tion). STRIDE-specific code will be licensed separately upon thesis completion.

---

## References

- **REVOL-E-TION**: https://github.com/TUMFTM/REVOL-E-TION
- **oemof-solph**: https://github.com/oemof/oemof-solph
- **Pyomo**: http://www.pyomo.org/

---

## Contact

**Arno Claude**
Master's Student, Technical University of Munich
Thesis Supervisor: Anna Paper (anna.paper@tum.de)
Email: arno.claude@googlemail.com