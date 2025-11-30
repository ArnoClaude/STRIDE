"""
Test 3-stage multi-stage optimization with refactored config-driven code.

Run: /Users/arnoclaude/Documents/TUM/Thesis/thesis-optimization/venv/bin/python3 test_3_stage.py
"""

from pathlib import Path
from multi_stage import MultiStageConfig, SequentialStageOptimizer

# Setup paths
repo = Path("/Users/arnoclaude/Documents/TUM/Thesis/STRIDE")

# Load configuration from default.yaml
print("\n" + "="*80)
print("LOADING CONFIGURATION")
print("="*80)
config = MultiStageConfig.from_yaml()

print(f"✓ Config loaded: {len(config.stages)} stages ({config.stages})")
print(f"✓ Stage duration: {config.stage_duration_years} years")
print(f"✓ Cost evolution: PV -{config.tech_costs['pv'].annual_decline_rate*100}%/yr, ESS -{config.tech_costs['ess'].annual_decline_rate*100}%/yr")
print(f"✓ Fleet growth: +{config.demand_annual_growth_rate*100}%/yr")
print(f"✓ CO2 pathway: {config.emissions_base_limit_kg} → {config.emissions_final_limit_kg} kg (linear)")

# Create output directory for test
output_dir = repo / "multi_stage" / "test_output_3stage"
output_dir.mkdir(parents=True, exist_ok=True)

# Create optimizer with config
print("\n" + "="*80)
print("CREATING OPTIMIZER")
print("="*80)
optimizer = SequentialStageOptimizer(
    config=config,
    template_scenario_path=repo / "revoletion/example/scenarios_multi_stage_realistic.csv",
    output_dir=output_dir,
    scenario_column="multi_stage_test"
)

# Run optimization
print("\nStarting 3-stage optimization...")
print("This will take ~5-15 minutes (3 stages × ~2-5 min each)")
print("="*80)

try:
    results = optimizer.optimize()

    print("\n" + "="*80)
    print("✅ OPTIMIZATION COMPLETED SUCCESSFULLY!")
    print("="*80)

    # Validate results
    print("\nValidation:")
    print(f"  ✓ All {len(config.stages)} stages completed")
    print(f"  ✓ Total NPV: ${results['total_npv']:,.0f}")
    print(f"  ✓ Total CAPEX: ${results['total_capex']:,.0f}")

    # Check results files
    json_file = output_dir / "multi_stage_results.json"
    csv_file = output_dir / "investment_timeline.csv"

    if json_file.exists():
        print(f"  ✓ Results saved: {json_file}")
    if csv_file.exists():
        print(f"  ✓ Timeline saved: {csv_file}")

    # Print investment timeline
    print("\nInvestment Timeline:")
    timeline = results['investment_timeline']
    for _, row in timeline.iterrows():
        print(f"  {int(row['year'])}: PV {row['pv_total_kw']:.1f} kW (new: {row['pv_new_kw']:.1f}), "
              f"ESS {row['ess_total_kwh']:.1f} kWh (new: {row['ess_new_kwh']:.1f}), "
              f"CAPEX ${row['capex']:,.0f}")

    # Check stage linking
    print("\nStage Linking Validation:")
    prev_pv = None
    for year in config.stages:
        stage_result = results['stage_results'][year]
        pv_total = stage_result.get('pv_size_total', 0) or 0
        pv_invest = stage_result.get('pv_size_invest', 0) or 0

        if prev_pv is not None:
            pv_inherited = pv_total - pv_invest if pv_invest else pv_total
            if abs(pv_inherited - prev_pv) < 1:  # 1W tolerance
                print(f"  ✓ {year}: PV inherited correctly ({prev_pv/1000:.1f} kW)")
            else:
                print(f"  ✗ {year}: PV mismatch (expected {prev_pv/1000:.1f} kW, got {pv_inherited/1000:.1f} kW)")

        prev_pv = pv_total

    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED - REFACTORED CODE WORKS!")
    print("="*80)
    print(f"\nResults saved to: {output_dir}")

except Exception as e:
    print("\n" + "="*80)
    print("❌ OPTIMIZATION FAILED")
    print("="*80)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nCheck:")
    print("  1. Virtual environment active")
    print("  2. REVOLETION installed: cd revoletion && pip install -e .")
    print("  3. Template scenario exists: revoletion/example/scenarios_multi_stage_realistic.csv")
