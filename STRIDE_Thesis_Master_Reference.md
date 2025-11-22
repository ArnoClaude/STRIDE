# STRIDE Multi-Stage Depot Electrification Thesis - Master Reference Document

**Student:** Arno Claude
**Institution:** TUM (Technical University of Munich)  
**Supervisor:** Anna Paper (Prof. Dr.-Ing. M. Lienkamp)  
**Duration:** 6 months (roughly 60-90 pages)  
**Started:** 13.10.2025
**Expected Completion:** 13.04.2026

---

## Executive Summary

**Thesis Title:** "Multi-Stage Linear Optimization of Energy Components at Freight Forwarding Depots for Electric Trucks"

**Core Contribution:** Developing a sequential multi-stage optimization framework that extends REVOL-E-TION to plan infrastructure investments (PV, battery storage, chargers) over a 30-year horizon (2025-2055) for electric freight truck depots.

**Key Insight:** The thesis value lies NOT in algorithmic complexity but in comprehensive analysis, realistic scenarios, and actionable insights for freight companies transitioning to electric fleets.

---

## 1. Thesis Scope & Positioning

### 1.1 Research Question
How should freight depot operators optimally time and size infrastructure investments (PV, battery storage, charging equipment, grid connections) over 30 years to minimize costs while meeting electric fleet requirements?

### 1.2 What This Thesis IS
- ✅ Sequential multi-stage investment planning framework
- ✅ Extension of existing REVOL-E-TION framework
- ✅ Comprehensive scenario analysis and sensitivity studies
- ✅ Practical recommendations for freight industry
- ✅ Solid engineering master's thesis demonstrating competence

### 1.3 What This Thesis IS NOT
- ❌ Novel optimization algorithm development (PhD-level)
- ❌ Full stochastic programming (too complex for 6 months)
- ❌ Modification of REVOL-E-TION core (use as black box)
- ❌ Real-time operational control system

### 1.4 Research Gap
Existing literature lacks multi-stage planning frameworks for depot electrification that:
- Consider infrastructure investment timing over decades
- Account for technology cost declines
- Handle fleet growth and demand evolution
- Integrate solar PV and stationary storage

---

## 2. Methodology Overview

### 2.1 Approach: Sequential Multi-Stage Optimization

**Core Algorithm (Simplified):**
```python
for stage_year in [2025, 2030, 2035, 2040, 2045, 2050]:
    # 1. Set size_existing from previous stage results
    # 2. Update parameters (costs, demand, fleet size)
    # 3. Run REVOL-E-TION optimization
    # 4. Extract optimized capacities
    # 5. Store results for next stage
```

**Key Features:**
- **Sequential** (myopic) rather than simultaneous optimization
- More realistic - companies don't have perfect foresight
- Computationally tractable
- Allows re-evaluation at each stage with updated information

### 2.2 Why Sequential is Appropriate

**Advantages:**
- Reflects real-world decision-making under uncertainty
- Allows adaptation to actual conditions at each stage
- Computationally feasible within master's thesis timeline
- Easier to explain to industry stakeholders

**Justification for Anna:**
> "We employ a sequential multi-stage optimization approach that reflects real-world decision-making under uncertainty, where infrastructure investments are made based on current conditions and updated as new information becomes available."

### 2.3 Operational Optimization via REVOL-E-TION

**REVOL-E-TION provides:**
- Mixed-Integer Linear Programming (MILP) formulation
- Hourly dispatch optimization
- Component sizing within each stage
- NPV calculations
- Integration of: PV, stationary battery (ESS), grid connection, EV chargers, vehicle batteries (BEV)

**Your integration:**
- Wrapper layer calls REVOL-E-TION per stage
- Feeds forward capacity decisions
- Aggregates multi-stage NPV

### 2.4 Decision Variables (Per Stage)

**Investment decisions:**
- PV capacity additions [kW]
- Stationary battery capacity additions [kWh]
- Charger quantity additions [units]
- Grid connection capacity upgrades [kW]

**Constraints:**
- Capacity non-decreasing: `size_stage_N+1 ≥ size_stage_N`
- Optional: Budget constraints per stage
- Optional: Maximum growth rates
- Optional: Maximum CO2 emissions
- Optional: Maximum depot space used (for solar panels, wind turbines, etc.)

---

## 3. Repository Structure

```
arno-thesis-multi-stage-depot/
├── README.md
├── requirements.txt
├── .gitignore
│
├── revoletion/              # Git submodule (REVOL-E-TION)
│   └── (original code)
│
├── multi_stage/             # YOUR NEW CODE
│   ├── __init__.py
│   ├── sequential_optimizer.py   # Main wrapper
│   ├── scenario_builder.py       # Generate stage scenarios
│   ├── results_parser.py          # Parse REVOL-E-TION outputs
│   └── economics.py               # Multi-stage NPV calculations
│
├── analysis/                # YOUR ANALYSIS CODE
│   ├── __init__.py
│   ├── visualizations.py          # Investment timeline plots
│   ├── comparison.py              # Scenario comparisons
│   └── sensitivity.py             # Sensitivity analyses
│
├── case_studies/            # Realistic depot scenarios
│   ├── baseline/
│   ├── high_growth/
│   └── conservative/
│
├── notebooks/               # Jupyter notebooks
│   ├── 01_revoletion_exploration.ipynb
│   ├── 02_multi_stage_prototype.ipynb
│   └── 03_results_analysis.ipynb
│
├── docs/                    # Thesis documentation
│   ├── methodology.md
│   ├── formulation.tex
│   └── figures/
│
└── results/                 # Output directory
```

---

## 4. REVOL-E-TION Key Learnings

### 4.1 Architecture Understanding

**Core Concepts:**
- **Blocks:** Modular components (PVSource, StationaryEnergyStorage, GridConnection, VehicleCommoditySystem)
- **Strategies:** 
  - `go` (global optimum) - Single optimization for entire period
  - `rh` (rolling horizon) - Sequential optimizations with sliding window
- **Temporal Structure:**
  - `sim_duration` (e.g., 50 days) - Simulation period
  - `prj_duration` (e.g., 25 years) - Project lifetime
  - Results extrapolated from simulation to project duration

**Available Components:**
- ✅ PVSource (solar panels)
- ✅ StationaryEnergyStorage (stationary batteries)
- ✅ GridConnection (grid with bidirectional flow)
- ✅ VehicleCommoditySystem (EVs with V2G)
- ✅ BatteryCommoditySystem (mobile batteries)
- ✅ FixedDemand (depot base load)

### 4.2 Key Parameters

**Investment Control:**
```csv
component,size_existing,0           # Current capacity
component,size_max,None             # No upper limit
component,invest,True               # Enable optimization
component,capex_spec,0.5            # Cost per unit capacity
```

**Economic Parameters:**
```csv
scenario,wacc,0.09                  # Discount rate (9%)
scenario,prj_duration,25            # Project lifetime (years)
scenario,sim_duration,50            # Simulation period (days)
```

### 4.3 Results Interpretation

**From Summary CSV:**
- `size_total` = Total installed capacity (existing + additional)
- `size_additional` = Optimized capacity additions
- `npv` = Net Present Value
- `lcoe_total` = Levelized Cost of Energy ($/Wh, multiply by 1000 for ¢/kWh)
- `capex_sim` = Capital expenditure in simulation period
- `opex_sim` = Operational expenditure in simulation period

**Example Results (from test run):**
- ICEV baseline: LCOE = 20.48 ¢/kWh
- BEV_GRID: LCOE = 17.77 ¢/kWh (EVs cheaper than diesel)
- BEV_MG (with PV): LCOE = 15.65 ¢/kWh (PV reduces costs further)

### 4.4 Why Cyan and Purple Lines Are Opposite

**Energy Balance Principle:**
- Cyan (demand) = negative = energy consumption
- Purple (grid) = positive = energy supply
- Grid supplies exactly what demand needs: `Grid Power = -Demand Power`

---

## 5. Literature Review Framework

### 5.1 30-Dimension Analysis Template

**Core Categories:**
1. **Problem Characteristics:** Single vs multi-period, deterministic vs stochastic
2. **Methodology:** MILP vs simulation vs heuristic
3. **Temporal Structure:** Multi-period (hourly decisions) vs multi-stage (investment periods)
4. **Components:** PV, battery, chargers, grid, transformers
5. **Objectives:** Cost minimization, emissions, reliability
6. **Constraints:** Budget, capacity, power limits
7. **Uncertainty Handling:** Scenarios, robust optimization, stochastic programming
8. **Case Studies:** Scale, location, validation
9. **Gaps Identified:** What's missing in current literature

### 5.2 Key Papers Analyzed

1. **Bakker et al. (2025):** Fleet replacement and charging infrastructure
2. **Li & Alaküla (2024):** Terminal capacity expansion planning  
3. **Zahedi et al. (2025):** Heavy-duty EV charging station sizing with uncertainty
4. **Lerbinger (MANGOever):** Munich depot case study
5. Additional papers on multi-stage optimization, EV charging, depot planning

### 5.3 Research Gap Summary

**What exists:**
- Single-period depot optimization
- Multi-period operational scheduling
- Fleet replacement planning

**What's missing (YOUR CONTRIBUTION):**
- Multi-stage infrastructure investment planning over 30 years
- Integration of technology cost declines
- Coordination of PV, battery, and charging investments
- Practical decision support for phased electrification

---

## 6. Implementation Timeline & Progress

### ✅ Completed (Weeks 1-4)

**REVOL-E-TION Integration & Understanding (2 weeks)**
- ✅ REVOL-E-TION cloned as git submodule
- ✅ Architecture exploration (blocks, strategies, temporal structure)
- ✅ Test runs with example scenarios
- ✅ Results interpretation methodology established

**CO2 Emission Constraint Implementation (1.5 weeks)**
- ✅ Extended `constraints.py` with `limit_co2_emissions()` method
- ✅ Added `co2_spec_g2s` parameter to GridMarket in `blocks.py`
- ✅ Validation notebook created: `01_test_co2_constraint.ipynb`
- ✅ Discovered and fixed simulation vs project period mismatch
- ✅ Verified constraint working correctly (7 scenarios tested)

**Notebook Infrastructure (0.5 weeks)**
- ✅ Reorganized notebooks directory (each notebook in own subdirectory)
- ✅ Created `notebooks/README.md` with usage documentation
- ✅ Set up automated output management (plots, CSVs, JSON)
- ✅ Repository README created with installation instructions

---

### 🚧 Current: Multi-Stage Sequential Optimizer (3 weeks)

**Phase 1A: Basic 2-Stage Optimizer (2 weeks)**
- 🔨 Implement `SequentialStageOptimizer` class
- 🔨 Implement basic `ScenarioBuilder` with stage linking
- 🔨 Implement basic `ResultsParser`
- 🔨 Test 2-stage optimization (2025 → 2030)
- **Deliverable:** Working 2-stage optimizer with capacity linking

**Phase 1B: Full 6-Stage + Cost Curves (1 week)**
- Extend to 6 stages (2025-2050)
- Implement technology cost decline curves
- Multi-stage NPV aggregation
- Validation notebook: `02_test_sequential_optimizer.ipynb`
- **Deliverable:** Complete 6-stage optimizer with declining costs

---

### 📅 Upcoming Phases

**Case Studies & Data (3-4 weeks)**
- Define 3 depot cases (small/medium/large)
- Gather realistic data (fleet profiles, tariffs, costs)
- Run baseline scenarios
- Generate scenario variations (optimistic/baseline/pessimistic)
- **Deliverable:** Complete case study results

**Analysis & Visualization (3 weeks)**
- Investment timeline plots
- NPV waterfall charts
- Sensitivity analyses (5 key parameters)
- Scenario comparisons
- **Deliverable:** 15-20 publication-quality figures

**Thesis Writing (8-10 weeks, parallel with above)**
- Methodology chapter (2 weeks)
- Results chapter (3 weeks)
- Introduction & literature (2 weeks)
- Conclusions (1 week)
- Assembly & revision (2 weeks)
- **Deliverable:** Complete draft (~85-90 pages)

**Final Revision & Submission (2-3 weeks)**
- Incorporate supervisor feedback
- Final polish and formatting
- **Deliverable:** Submitted thesis

**Expected completion: 13.04.2026**

---

## 7. Critical Success Factors

### 7.1 Must-Have Milestones

- **End of Phase 1A:** Working 2-stage optimizer (2025 → 2030)
- **End of Phase 1B:** Complete 6-stage optimizer with cost curves
- **End of Case Studies:** 3 complete depot scenarios analyzed
- **End of Analysis:** All figures and sensitivity studies complete
- **End of Writing:** Complete draft submitted to supervisor
- **Final:** Thesis submitted (13.04.2026)

### 7.2 Keys to Success

1. **No scope creep** - Resist "just one more feature"
2. **Weekly supervisor check-ins** - Catch issues early
3. **Iterative writing** - Don't wait until end to write
4. **Code as you go** - Document while implementing
5. **Parallel work** - Write methods while code runs
6. **"Good enough" mindset** - Master's thesis, not PhD

---

## 8. Data Requirements

### 8.1 What You CANNOT Use (Example Data is Inadequate)

REVOL-E-TION example data is toy data:
- 5 generic vehicles
- Generic demand profile  
- 50 days in Munich 2018
- Generic electricity prices

### 8.2 What You NEED (Realistic Depot Data)

**Fleet Profiles:**
- Real truck arrival/departure patterns
- Daily mileage distributions
- Charging requirements
- Growth projections (5-15% per year)

**Electricity Tariffs:**
- Real German/EU commercial tariffs
- Demand charges
- Time-of-use pricing
- Future price projections

**Technology Costs:**
- PV cost trajectories (e.g., NREL projections: -3% to -7% per year)
- Battery cost trajectories (e.g., BNEF projections: -5% to -10% per year)
- Charger costs
- Grid connection upgrade costs

**Depot Characteristics:**
- Location (for solar irradiance)
- Available space for PV
- Grid connection capacity and costs
- Existing infrastructure

**Future Scenarios:**
- Optimistic: Fast cost decline, high fleet growth
- Baseline: Moderate assumptions
- Pessimistic: Slow cost decline, constrained growth

### 8.3 Data Sources

- Research group existing projects (ask Anna)
- Literature (papers you reviewed often have data)
- Public databases (PVGIS for solar, Eurostat for prices)
- Industry reports (BNEF, IEA, NREL)
- Assumptions validated against literature

---

## 9. Thesis Structure (85-90 pages)

### Chapter 1: Introduction (~10 pages)
- Motivation (EU CO2 targets, freight electrification challenges)
- Problem statement
- Research questions
- Thesis objectives
- Structure overview

### Chapter 2: Literature Review (~15-20 pages)
- Multi-stage optimization approaches
- EV depot charging optimization
- Infrastructure planning under uncertainty
- Research gap identification
- Positioning of your work

### Chapter 3: Methodology (~12-15 pages)
**Section 3.1: Problem Formulation (3-4 pages)**
- Decision variables
- Objective function (NPV minimization)
- Constraints
- Mathematical notation

**Section 3.2: Multi-Stage Framework (2-3 pages)**
- Stage definition
- Sequential optimization approach
- Capacity feeding mechanism
- Flow diagram

**Section 3.3: Operational Optimization (2-3 pages)**
- REVOL-E-TION overview
- Integration approach
- Representative periods

**Section 3.4: Input Data (2-3 pages)**
- Fleet growth assumptions
- Cost projections
- Depot characteristics
- Data validation

**Section 3.5: Implementation (2-3 pages)**
- Software stack
- Computational approach
- Stage sequencing

### Chapter 4: Case Studies & Results (~25-30 pages)
**Section 4.1: Case Study Definitions (3-4 pages)**
- Small depot (20 trucks)
- Medium depot (50 trucks)
- Large depot (100 trucks)

**Section 4.2: Baseline Results (5-6 pages)**
- Investment timelines
- NPV comparisons
- Key insights per case

**Section 4.3: Scenario Analysis (6-8 pages)**
- Optimistic scenario
- Baseline scenario
- Pessimistic scenario
- Comparative analysis

**Section 4.4: Sensitivity Analysis (6-8 pages)**
- PV cost sensitivity
- Battery cost sensitivity
- Electricity price sensitivity
- Fleet growth sensitivity
- Discount rate sensitivity

**Section 4.5: Discussion (4-5 pages)**
- Interpretation of results
- Investment timing recommendations
- Practical implications
- Limitations

### Chapter 5: Conclusions (~5 pages)
- Summary of findings
- Main contributions
- Limitations
- Future work
- Closing remarks

**Total: ~70-85 pages + references/appendices = 90 pages**

---

## 10. Key Visualizations to Create

### 10.1 Investment Timeline Plots
- Stacked bar chart: Capacity additions by stage
- X-axis: Years (2025, 2030, 2035...)
- Y-axis: Capacity (kW or kWh)
- Stacks: PV, Battery, Chargers, Grid
- One plot per scenario

### 10.2 NPV Waterfall Charts
- Breakdown of NPV components
- Initial investment
- Stage-wise CAPEX
- Operational savings
- Final NPV
- Compare scenarios

### 10.3 Scenario Comparison
- Side-by-side investment paths
- Optimistic vs baseline vs pessimistic
- Show divergence over time
- Cost comparison

### 10.4 Sensitivity Heatmaps
- 2D heatmap: Parameter variation vs NPV
- Parameters: PV cost, battery cost, electricity price, fleet growth
- Color: NPV value
- Identify critical parameters

### 10.5 Cost Breakdown
- Pie charts: CAPEX vs OPEX
- Component cost shares
- Per stage and cumulative

### 10.6 Operational Metrics
- Selected dispatch examples
- Peak load reduction
- Self-consumption rates
- Grid utilization

### 10.7 Comparison Plots
- Multi-stage vs single-stage investment
- Sequential vs upfront investment
- ROI timelines

---

## 11. Common Pitfalls to Avoid

### 11.1 Technical Pitfalls

**❌ Scope creep:** Adding transformer models, demand response, V2G revenue optimization, etc.
- **✅ Solution:** Stick to core: PV, battery, chargers, grid. That's enough.

**❌ Over-engineering:** Building perfectly general framework
- **✅ Solution:** Build for your specific use case. Generalization is PhD work.

**❌ Getting stuck on REVOL-E-TION details:** Trying to modify core
- **✅ Solution:** Treat as black box. Use what's there.

**❌ Analysis paralysis:** Trying to make perfect data
- **✅ Solution:** Use reasonable assumptions, validate against literature, move on.

### 11.2 Writing Pitfalls

**❌ Over-explaining operational optimization:** 20 pages on MILP
- **✅ Solution:** 2-3 pages citing REVOL-E-TION paper. Focus on YOUR contribution.

**❌ Under-explaining decisions:** "We chose 7 stages"
- **✅ Solution:** Justify every choice with reasoning or literature.

**❌ Results without interpretation:** Just tables of numbers
- **✅ Solution:** Every figure needs 1-2 paragraphs explaining what it means and why it matters.

**❌ Missing the "so what?":** Technical results without practical implications
- **✅ Solution:** Always connect to real-world decisions: "This means depot operators should..."

### 11.3 Project Management Pitfalls

**❌ Writing only at the end:** Nothing written until Month 5
- **✅ Solution:** Write methods in Month 2-3, results in Month 4, assemble in Month 5.

**❌ No supervisor alignment:** Building wrong thing for 3 months
- **✅ Solution:** Show Anna progress every 2-3 weeks. Get explicit approval.

**❌ Underestimating data work:** "I'll just use example data"
- **✅ Solution:** Start data gathering in Week 8-9. Takes longer than you think.

**❌ No backup plan:** All eggs in one case study
- **✅ Solution:** Have 3 case studies. If one fails, you have two others.

---

## 12. Quick Reference Commands

### 12.1 Running REVOL-E-TION
```bash
# Navigate to REVOL-E-TION directory
cd ~/Documents/TUM/Thesis/STRIDE/revoletion

# Activate virtual environment
source ../venv/bin/activate

# Run all scenarios
python3 -m revoletion.main \
  --settings example/settings.csv \
  --scenario example/scenarios_example.csv

# Run specific scenario (create custom CSV with only desired columns)
python3 -m revoletion.main \
  --settings case_studies/baseline/settings.csv \
  --scenario case_studies/baseline/scenario_2025.csv
```

### 13.2 Finding Results
```bash
# Results directory
cd revoletion/results/

# Most recent results
ls -lt | head

# Open summary CSV
cd <most_recent_results_dir>
open *_summary.csv  # macOS
xdg-open *_summary.csv  # Linux
```

### 13.3 Git Workflow
```bash
# Initial setup (REVOL-E-TION as submodule)
cd ~/Documents/TUM/Thesis/STRIDE
git submodule add https://github.com/TUMFTM/REVOL-E-TION.git revoletion

# Update submodule
git submodule update --remote revoletion
```

---

## 14. Essential Literature References

### 14.1 Core Papers for Your Thesis

1. **Bakker et al. (2025)** - Strategic fleet replacement for electrification
   - Multi-period fleet and infrastructure planning
   - MILP formulation
   - Good example of phased approach

2. **Li & Alaküla (2024)** - Terminal capacity expansion planning
   - Multi-stage investment optimization
   - Logistics terminal context
   - Similar problem structure

3. **Zahedi et al. (2025)** - Heavy-duty EV charging station sizing
   - Uncertainty modeling (your potential extension)
   - Multi-period expansion with scenarios
   - Framework approach applicable to depots

4. **REVOL-E-TION Paper** (Under review at SSRN)
   - Your foundational tool
   - Must cite extensively in methodology
   - DOI: 10.2139/ssrn.5127283

### 14.2 Supporting Literature

- Multi-stage optimization methodologies
- Technology cost projection reports (NREL, BNEF, IEA)
- EU emissions reduction targets and policies
- Freight electrification challenges and economics
- Solar PV and battery storage integration

---

## 15. Final Reminders & Motivation

### 15.1 What Success Looks Like

✅ Working multi-stage optimizer by Week 7  
✅ 3 complete case studies with realistic data  
✅ 5-7 sensitivity analyses  
✅ 15-20 publication-quality figures  
✅ 85-90 page thesis with clear narrative  
✅ Actionable recommendations for industry  
✅ Code repository on GitHub  
✅ Submitted by 13.04.2026

### 15.2 Core Message for Your Thesis

> "This thesis demonstrates that sequential multi-stage optimization enables freight depot operators to optimally time infrastructure investments over 30 years, reducing total costs by X-Y% compared to single-stage approaches, while adapting to evolving technology costs and fleet requirements."

### 15.3 Remember

- **The code is the tool, not the contribution**
- **Analysis, insights, and recommendations are the real value**
- **"Good enough" is better than perfect**
- **Stay focused on the core problem**
- **Show Anna progress every 2-3 weeks**

---

## Document Control

**Created:** 01.11.2025
**Last Updated:** 22.11.2025
**Version:** 1.1
**Contact:** Arno (TUM Master's Student)
**Supervisor:** Anna Paper (Prof. Dr.-Ing. M. Lienkamp)

**Changelog:**
- v1.1 (22.11.2025): Updated timeline with completed work (CO2 constraint, notebook infrastructure), removed week-based counting
- v1.0 (17.11.2025): Initial version

---

**END OF MASTER REFERENCE DOCUMENT**
