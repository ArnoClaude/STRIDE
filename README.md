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

## Development Status

- ✅ REVOL-E-TION integration and understanding
- ✅ CO2 constraint implementation and validation
- ✅ Multi-stage optimizer development
- 🚧 Data collection (CURRENT)
- 📅 Case studies and sensitivity analysis
- 📅 Thesis writing

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

---

*Last updated: November 2025*
