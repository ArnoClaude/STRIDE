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

## Project Structure

```
STRIDE/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── revoletion/                  # REVOL-E-TION submodule (DO NOT MODIFY)
│   ├── revoletion/             # Core optimization framework
│   │   ├── blocks.py           # Energy system components (PV, ESS, chargers)
│   │   ├── constraints.py      # Custom constraints (incl. CO2 limits)
│   │   ├── simulation.py       # Optimization execution
│   │   └── ...
│   ├── example/                # Example configurations
│   │   ├── scenarios_example.csv
│   │   └── settings.csv
│   └── results/                # Optimization outputs
├── multi_stage/                # STRIDE-specific code (IN DEVELOPMENT)
│   ├── sequential_optimizer.py # Multi-stage wrapper
│   ├── scenario_builder.py     # Technology cost projections
│   └── results_parser.py       # Results aggregation
└── notebooks/                  # Validation notebooks
    ├── 01_test_co2_constraint.ipynb  # CO2 constraint verification
    └── output/                 # Plots and exports
```

---

## Usage

### Running REVOL-E-TION (Single-Stage)

To run a basic single-stage optimization:

```bash
cd revoletion
python -m revoletion.main \
    --settings example/settings.csv \
    --scenario example/scenarios_example.csv
```

Results will be saved to `revoletion/results/TIMESTAMP_scenarios_example/`.

### Validation Notebooks

Notebooks in `notebooks/` verify individual STRIDE components:

- **`01_test_co2_constraint.ipynb`**: Validates CO2 emission constraint implementation across multiple emission limits

To run notebooks:
```bash
jupyter notebook notebooks/01_test_co2_constraint.ipynb
```

**Note:** Ensure Jupyter is using the venv kernel (see Installation section).

### Multi-Stage Optimization (In Development)

The multi-stage optimizer is under active development:

```bash
python multi_stage/sequential_optimizer.py --config config.yaml
```

---

## CO2 Emission Constraints

STRIDE extends REVOL-E-TION with optional CO2 emission limits. To use:

1. **Set grid emission factor** in scenario CSV:
   ```csv
   block,key,scenario_name
   grid,co2_spec_g2s,0.4
   ```
   Default: 0.4 kg CO2/kWh (German grid average)

2. **Set CO2 budget** in scenario CSV:
   ```csv
   block,key,scenario_name
   scenario,co2_max,10000
   ```
   Units: kg CO2 over simulation period. Use `None` or omit for unlimited.

3. **Run optimization** as normal - the constraint is applied automatically.

See `notebooks/01_test_co2_constraint.ipynb` for validation examples.

---

## Development Status

- ✅ **Week 1-3**: REVOL-E-TION integration and understanding
- ✅ **Week 3-4**: CO2 constraint implementation and validation
- 🚧 **Week 4-7**: Multi-stage optimizer development (CURRENT)
- 📅 **Week 8-12**: Case studies and sensitivity analysis
- 📅 **Week 13-16**: Thesis writing

---

## Contributing

This is a thesis project and is not currently accepting external contributions. For questions or collaboration inquiries, please contact the author.

---

## License

This project uses REVOL-E-TION as a submodule, which is licensed under [its own terms](https://github.com/tum-ens/revol-e-tion). STRIDE-specific code will be licensed separately upon thesis completion.

---

## References

- **REVOL-E-TION**: https://github.com/tum-ens/revol-e-tion
- **oemof-solph**: https://github.com/oemof/oemof-solph
- **Pyomo**: http://www.pyomo.org/

---

## Contact

**Arno Claude**
Master's Student, Technical University of Munich
Thesis Supervisor: [To be added]
Email: [To be added]

---

*Last updated: November 2025*
