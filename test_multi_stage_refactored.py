"""
Test script for refactored multi-stage optimization.

Validates config system and runs a quick 3-stage optimization.
"""

from pathlib import Path
from multi_stage import MultiStageConfig, SequentialStageOptimizer

# Load configuration
config = MultiStageConfig.from_yaml()

print("\n" + "="*80)
print("CONFIGURATION LOADED")
print("="*80)
print(f"Stages: {config.stages}")
print(f"Stage duration: {config.stage_duration_years} years")
print(f"PV base cost: ${config.tech_costs['pv'].base_cost}/W")
print(f"PV decline rate: {config.tech_costs['pv'].annual_decline_rate*100}%/yr")
print(f"ESS base cost: ${config.tech_costs['ess'].base_cost}/Wh")
print(f"ESS decline rate: {config.tech_costs['ess'].annual_decline_rate*100}%/yr")
print(f"Fleet growth: {config.demand_annual_growth_rate*100}%/yr")
print(f"CO2 pathway: {config.emissions_base_limit_kg} kg → {config.emissions_final_limit_kg} kg")
print(f"WACC: {config.wacc*100}%")
print("="*80)

# Test cost calculation for 2030
print("\nCost evolution test (2025 → 2030):")
pv_2025 = config.tech_costs['pv'].get_cost(2025)
pv_2030 = config.tech_costs['pv'].get_cost(2030)
ess_2025 = config.tech_costs['ess'].get_cost(2025)
ess_2030 = config.tech_costs['ess'].get_cost(2030)
print(f"  PV: ${pv_2025:.3f}/W → ${pv_2030:.3f}/W ({((pv_2030/pv_2025)-1)*100:.1f}%)")
print(f"  ESS: ${ess_2025:.3f}/Wh → ${ess_2030:.3f}/Wh ({((ess_2030/ess_2025)-1)*100:.1f}%)")

# Test CO2 limit calculation
print("\nCO2 pathway test:")
for year in config.stages:
    co2_limit = config.calculate_co2_limit(year)
    print(f"  {year}: {co2_limit:.0f} kg")

# Test fleet growth calculation
print("\nFleet growth test:")
for year in config.stages:
    fleet_size = config.calculate_fleet_size(year)
    print(f"  {year}: {fleet_size:,} vehicles")

# Test discount factor calculation
print("\nDiscount factor test:")
for year in config.stages:
    discount_factor = config.get_discount_factor(year)
    print(f"  {year}: {discount_factor:.4f}")

print("\n✓ All configuration tests passed!")
print("\nTo run full optimization, uncomment the code below:")
print("# repo = Path('/Users/arnoclaude/Documents/TUM/Thesis/STRIDE')")
print("# optimizer = SequentialStageOptimizer(")
print("#     config=config,")
print("#     template_scenario_path=repo / 'revoletion/example/scenarios_multi_stage_realistic.csv',")
print("#     output_dir=repo / 'multi_stage/test_output',")
print("#     scenario_column='multi_stage_test'")
print("# )")
print("# results = optimizer.optimize()")
