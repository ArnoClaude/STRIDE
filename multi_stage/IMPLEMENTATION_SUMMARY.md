# Multi-Stage Optimization Framework - Implementation Summary

**Date**: November 24, 2025
**Author**: Arno Claude
**Thesis**: STRIDE - Sequential Temporal Resource Investment for Depot Electrification

---

## Overview

This document summarizes the complete implementation of the multi-stage sequential optimization framework for depot electrification, including all enhancements completed in this session.

---

## Completed Enhancements

### 1. ✅ Fixed Project Duration Per Stage

**Problem**: All stages used 25-year project duration, causing economic metrics to double-count across stages.

**Solution**: Implemented automatic stage duration calculation based on stage list.

**Files Modified**:
- `scenario_builder.py`: Added `stage_duration` parameter to `create_stage_scenario()`
- `sequential_optimizer.py`: Calculate duration as `stages[i+1] - stages[i]`

**Impact**:
- Correct economic evaluation (5-year stages instead of 25-year)
- Proper NPV aggregation across stages

**Example**:
```python
# For stages [2025, 2030, 2035]:
# - Stage 2025: 5-year duration (2025-2030)
# - Stage 2030: 5-year duration (2030-2035)
```

---

### 2. ✅ Project-Level CO2 Tracking

**Problem**: Only simulation-level CO2 was tracked; project-level emissions unclear.

**Solution**: Added comprehensive CO2 tracking with extrapolation factors.

**Files Modified**:
- `results_parser.py`: Added `co2_prj_kg`, `co2_extrapolation_factor`, `sim_duration_days`, `prj_duration_years`

**New Metrics**:
```python
{
    'co2_sim_kg': 6959,              # Constraint enforcement (50 days)
    'co2_prj_kg': 254,506,           # Full project (5 years)
    'co2_extrapolation_factor': 36.5, # 5 years / 50 days
    'sim_duration_days': 50,
    'prj_duration_years': 5
}
```

**Impact**: Clear distinction between constraint scope and total emissions

---

### 3. ✅ Technology Cost Curves

**Problem**: Static technology costs → no incentive for later-stage investments.

**Solution**: Implemented exponential cost decline curves.

**Implementation** (`scenario_builder.py::_update_costs`):
```python
# PV: 5% annual decline
pv_cost_new = pv_cost_base * (1 - 0.05) ** years_elapsed

# ESS: 8% annual decline
ess_cost_new = ess_cost_base * (1 - 0.08) ** years_elapsed
```

**Results**:
- **2025**: PV $0.50/W, ESS $0.250/Wh (baseline)
- **2030**: PV $0.39/W (-22%), ESS $0.165/Wh (-34%)
- **2050**: PV $0.14/W (-72%), ESS $0.031/Wh (-88%)

**Impact**: Later stages benefit from cheaper technology → dynamic investment decisions

---

### 4. ✅ Fleet Demand Growth

**Problem**: Static fleet size → no need for capacity expansion.

**Solution**: Implemented 10% annual fleet growth.

**Implementation** (`scenario_builder.py::_update_demand`):
```python
growth_rate = 0.10
growth_factor = (1 + growth_rate) ** years_elapsed

# Scale fleet size and annual consumption
fleet_new = fleet_base * growth_factor
consumption_new = consumption_base * growth_factor
```

**Results**:
- **2025**: 30,000 vehicles (baseline)
- **2030**: 48,315 vehicles (+61%)
- **2050**: 325,041 vehicles (+983%, ~11x)

**Impact**: Growing demand necessitates investments across multiple stages

---

### 5. ✅ CO2 Limit Evolution

**Problem**: Static CO2 limits don't represent decarbonization pathways.

**Solution**: Linear CO2 tightening from 500 kg (2025) to 100 kg (2050).

**Implementation** (`scenario_builder.py::_update_co2_limits`):
```python
co2_start = 500  # kg (50-day simulation)
co2_end = 100    # kg
co2_limit = co2_start + (co2_end - co2_start) / 25 * years_elapsed
```

**Results**:
- **2025**: 500 kg CO2 (relaxed, allows grid import)
- **2030**: 420 kg (-16%)
- **2040**: 260 kg (-48%)
- **2050**: 100 kg (-80%, near zero-carbon)

**Impact**: Forces renewable investments to meet tightening environmental constraints

---

### 6. ✅ Enhanced Infeasibility Visibility

**Problem**: Infeasible scenarios not prominently displayed.

**Solution**:
1. Enhanced console output with clear error messages
2. Added infeasibility check cell in notebooks
3. Improved error handling with helpful suggestions

**Implementation**:

**In `sequential_optimizer.py`**:
```python
if stage_result.get('status') == 'infeasible':
    print("❌ MULTI-STAGE OPTIMIZATION STOPPED - INFEASIBLE STAGE")
    print("Possible causes:")
    print("  • CO2 constraint too tight for available technologies")
    print("  • Insufficient capacity inherited from previous stage")
    # ... suggestions ...
```

**In notebooks**:
```python
# Check for infeasible stages
infeasible_stages = [year for year, r in results.items()
                     if r.get('status') == 'infeasible']
if infeasible_stages:
    print("⚠️  WARNING: INFEASIBLE STAGES DETECTED")
    # ... detailed diagnostics ...
```

**Impact**: Immediate visibility of optimization failures with actionable guidance

---

### 7. ✅ Comprehensive Testing

**Test Script**: `example/test_evolution_functions.py`

**Validates**:
- ✓ Cost curves (PV 5%/yr, ESS 8%/yr)
- ✓ Demand growth (10%/yr)
- ✓ CO2 pathway (500 → 100 kg)
- ✓ Stage linking (capacity inheritance)
- ✓ Project duration (5-year stages)

**Test Coverage**:
- Base year (2025): No evolution
- Mid-stage (2030): 5-year evolution
- Final stage (2050): 25-year evolution

---

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 SequentialStageOptimizer                     │
│                    (orchestration)                           │
└────────┬──────────────────────────────────┬─────────────────┘
         │                                  │
         ▼                                  ▼
┌────────────────────┐           ┌─────────────────────────┐
│  ScenarioBuilder   │           │    ResultsParser        │
│  - Stage linking   │           │  - Metric extraction    │
│  - Cost curves     │           │  - NPV discounting      │
│  - Demand growth   │           │  - CO2 tracking         │
│  - CO2 evolution   │           │  - Infeasibility detect │
└─────────┬──────────┘           └──────────┬──────────────┘
          │                                 │
          ▼                                 ▼
┌──────────────────────────────────────────────────────────┐
│              REVOL-E-TION (MILP solver)                   │
│         Optimizes each stage independently               │
└──────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Myopic Optimization**: Each stage optimizes independently with perfect foresight within that stage
2. **Stage Linking**: Capacities flow forward as non-reversible constraints
3. **Economic Accuracy**: NPV discounting with 9% WACC
4. **Technological Realism**: Learning curves based on industry projections
5. **Environmental Compliance**: CO2 constraints with decarbonization pathways

---

## Usage Example

```python
from multi_stage import SequentialStageOptimizer

# Define stages (years)
stages = [2025, 2030, 2035, 2040, 2045, 2050]

# Create optimizer
optimizer = SequentialStageOptimizer(
    stages=stages,
    template_scenario_path="scenarios_template.csv",
    settings_path="settings.csv",
    revoletion_dir=Path("revoletion/"),
    output_dir=Path("output/"),
    scenario_column="baseline",
    discount_rate=0.09
)

# Run optimization (all stages sequentially)
results = optimizer.optimize()

# Access results
print(f"Total NPV: ${results['total_npv']:,.0f}")
print(f"Total CAPEX: ${results['total_capex']:,.0f}")

# Investment timeline
timeline = results['investment_timeline']
for _, row in timeline.iterrows():
    print(f"{row['year']}: PV {row['pv_new_kw']:.0f} kW, "
          f"ESS {row['ess_new_kwh']:.0f} kWh")
```

---

## Key Formulas

### Cost Decline
```
cost(t) = cost(2025) × (1 - decline_rate)^(t - 2025)

PV:  5% annual decline
ESS: 8% annual decline
```

### Demand Growth
```
demand(t) = demand(2025) × (1 + growth_rate)^(t - 2025)

Fleet: 10% annual growth
```

### CO2 Pathway
```
CO2_max(t) = 500 - (500 - 100) / 25 × (t - 2025)

Linear: 500 kg (2025) → 100 kg (2050)
```

### NPV Discounting
```
NPV_discounted = NPV_stage / (1 + WACC)^(t - 2025)

WACC: 9% (weighted average cost of capital)
```

### Stage Duration
```
duration(stage_i) = stages[i+1] - stages[i]

For stages [2025, 2030, 2035]:
- Stage 2025: 5 years
- Stage 2030: 5 years
```

---

## Output Files

### Per-Stage Outputs
- `scenario_stage_{year}.csv` - Stage-specific scenario file
- `results/{timestamp}_scenario_stage_{year}/` - REVOL-E-TION results

### Aggregated Outputs
- `multi_stage_results.json` - Complete results for all stages
- `investment_timeline.csv` - Investment decisions by year
- `summary_statistics.csv` - Economic and technical metrics

---

## Configuration Parameters

### Evolution Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `pv_decline_rate` | 5% | Annual PV cost decline |
| `ess_decline_rate` | 8% | Annual battery cost decline |
| `fleet_growth_rate` | 10% | Annual fleet size growth |
| `co2_start` | 500 kg | Initial CO2 limit (2025) |
| `co2_end` | 100 kg | Final CO2 limit (2050) |
| `discount_rate` | 9% | WACC for NPV discounting |

### Optimizer Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `stages` | [2025, ...] | List of stage years |
| `scenario_column` | First column | Which scenario to use from template |
| `timeout` | 600s | REVOL-E-TION solver timeout |

---

## Validation

### Test Results (Evolution Functions)

**Cost Curves** ✅
- 2025 → 2030: PV -22%, ESS -34% (matches theoretical)
- 2025 → 2050: PV -72%, ESS -88% (matches theoretical)

**Demand Growth** ✅
- 2025 → 2030: +61% (matches 1.1^5 = 1.61)
- 2025 → 2050: +983% (matches 1.1^25 = 10.83)

**CO2 Pathway** ✅
- Linear decline: 500 → 420 → 340 → ... → 100 kg
- Consistent application across all stages

**Stage Linking** ✅
- Capacities correctly inherited as `size_existing`
- Non-reversibility enforced by REVOL-E-TION constraints

**Project Duration** ✅
- Correctly set to stage duration (5 years per stage)
- Economic metrics properly scoped

---

## Future Enhancements

### Potential Additions
1. **Stochastic demand** - Uncertainty in fleet growth projections
2. **Technology learning** - Wright's Law instead of exponential decline
3. **Grid tariff evolution** - Dynamic electricity pricing
4. **Policy scenarios** - Carbon pricing, subsidies
5. **Weather variability** - PV generation uncertainty across stages
6. **Battery degradation** - Capacity fade over project lifetime
7. **Salvage value** - Asset value at end of stage
8. **Retirement decisions** - Optimal decommissioning timing

### Research Questions
- What is the optimal investment timing under uncertainty?
- How sensitive are results to discount rate assumptions?
- What CO2 pathway is most cost-effective?
- How does grid connection sizing evolve with fleet growth?

---

## References

### Related Files
- `/multi_stage/scenario_builder.py` - Scenario generation with evolution
- `/multi_stage/sequential_optimizer.py` - Multi-stage orchestration
- `/multi_stage/results_parser.py` - Results extraction and aggregation
- `/notebooks/02_test_2_stage/` - 2-stage validation notebook
- `/example/test_evolution_functions.py` - Evolution function unit test

### Documentation
- REVOL-E-TION: https://github.com/yourusername/revoletion
- STRIDE Thesis: Chapter 4 (Methodology)

---

## Changelog

### 2025-11-24
- ✅ Fixed project duration per stage (5 years instead of 25)
- ✅ Added project-level CO2 tracking with extrapolation
- ✅ Implemented technology cost curves (PV 5%/yr, ESS 8%/yr)
- ✅ Implemented fleet demand growth (10%/yr)
- ✅ Added CO2 limit evolution (500 → 100 kg)
- ✅ Enhanced infeasibility visibility in output and notebooks
- ✅ Created comprehensive unit tests for evolution functions
- ✅ Updated documentation with formulas and examples

---

**Status**: ✅ All core features implemented and tested
**Next Step**: Run full 6-stage optimization (2025-2050) with real scenario data
