"""
Quick test to verify stage evolution functions work correctly.
Tests cost curves, demand growth, and CO2 limit evolution.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_stage.scenario_builder import ScenarioBuilder

# Setup paths
repo = Path("/Users/arnoclaude/Documents/TUM/Thesis/STRIDE")
template_path = repo / "revoletion/example/scenarios_multi_stage_test.csv"
output_dir = repo / "example"

# Initialize builder
builder = ScenarioBuilder(template_path)

print("="*80)
print("Testing Stage Evolution Functions")
print("="*80)

# Test 2025 (base year - no evolution)
print("\n1. Testing Year 2025 (Base Year)")
print("-" * 60)
stage_2025 = builder.create_stage_scenario(
    stage_year=2025,
    output_path=output_dir / "test_scenario_2025.csv",
    previous_stage_results=None,
    scenario_column="multi_stage_test",
    stage_duration=5
)

# Test 2030 (5 years elapsed - should see evolution)
print("\n2. Testing Year 2030 (5 years elapsed)")
print("-" * 60)
print("Expected changes:")
print("  • PV cost: -22.6% (5% decline over 5 years)")
print("  • ESS cost: -34.0% (8% decline over 5 years)")
print("  • Fleet size: +61.1% (10% growth over 5 years)")
print("  • CO2 limit: 500 kg → 420 kg (linear decline)")
print()

# Simulate previous stage results
previous_results = {
    'pv_size_total': 359730.0,  # W
    'ess_size_total': 28108.0,   # Wh
    'grid_size_g2s': 106164.0,   # W
    'grid_size_s2g': 106164.0,   # W
}

stage_2030 = builder.create_stage_scenario(
    stage_year=2030,
    output_path=output_dir / "test_scenario_2030.csv",
    previous_stage_results=previous_results,
    scenario_column="multi_stage_test",
    stage_duration=5
)

# Test 2050 (25 years elapsed - maximum evolution)
print("\n3. Testing Year 2050 (25 years elapsed)")
print("-" * 60)
print("Expected changes:")
print("  • PV cost: -72.3% (5% decline over 25 years)")
print("  • ESS cost: -86.8% (8% decline over 25 years)")
print("  • Fleet size: +983.5% (10x, 10% growth over 25 years)")
print("  • CO2 limit: 500 kg → 100 kg (target reached)")
print()

stage_2050 = builder.create_stage_scenario(
    stage_year=2050,
    output_path=output_dir / "test_scenario_2050.csv",
    previous_stage_results=previous_results,
    scenario_column="multi_stage_test",
    stage_duration=5
)

print("\n" + "="*80)
print("✓ All evolution functions executed successfully!")
print("="*80)
print("\nGenerated test scenario files:")
print(f"  • {stage_2025}")
print(f"  • {stage_2030}")
print(f"  • {stage_2050}")
print("\nYou can inspect these files to verify the evolution logic.")
