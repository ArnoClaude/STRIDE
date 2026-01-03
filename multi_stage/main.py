#!/usr/bin/env python3
"""
STRIDE - Sequential Temporal Resource Investment for Depot Electrification

Multi-stage optimization CLI entry point.

Usage:
    python -m multi_stage.main --config CONFIG --scenario SCENARIO [--output OUTPUT]

Example:
    python -m multi_stage.main \
        --config multi_stage/config/schmid_test.yaml \
        --scenario revoletion/example_schmid/scenarios_schmid_test.csv \
        --output multi_stage/results/schmid_test
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="STRIDE: Multi-stage depot electrification optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 2-stage test
  python -m multi_stage.main \\
      --config configs/schmid_test.yaml \\
      --scenario inputs/schmid/scenarios.csv

  # Run 6-stage with CO2 constraints
  python -m multi_stage.main \\
      --config configs/schmid_6stage.yaml \\
      --scenario inputs/schmid/scenarios.csv
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to multi-stage YAML config file (e.g., configs/schmid_6stage.yaml)"
    )
    
    parser.add_argument(
        "--scenario", "-s",
        required=True,
        help="Path to base scenario CSV template (e.g., inputs/schmid/scenarios.csv)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory for results (default: from config file)"
    )
    
    parser.add_argument(
        "--scenario-column",
        default=None,
        help="Scenario column name to use from template (default: first column)"
    )
    
    args = parser.parse_args()
    
    # Validate paths
    config_path = Path(args.config)
    scenario_path = Path(args.scenario)
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    if not scenario_path.exists():
        print(f"❌ Scenario file not found: {scenario_path}")
        sys.exit(1)
    
    # Import here to avoid slow startup for --help
    from .config_loader import MultiStageConfig
    from .sequential_optimizer import SequentialStageOptimizer
    
    # Load config
    print(f"Loading config: {config_path}")
    config = MultiStageConfig.from_yaml(str(config_path))
    
    # Override output directory if specified
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = config.summary_output_dir
    
    # Print run summary
    print(f"\n{'='*60}")
    print(f"STRIDE Multi-Stage Optimization")
    print(f"{'='*60}")
    print(f"Config:   {config_path}")
    print(f"Scenario: {scenario_path}")
    print(f"Output:   {output_dir}")
    print(f"Stages:   {config.stages}")
    print(f"Fleet:    {config.demand_base_num_vehicles} vehicles (base)")
    print(f"Growth:   {config.demand_annual_growth_rate*100:.1f}%/yr")
    print(f"WACC:     {config.wacc*100:.1f}%")
    print(f"{'='*60}\n")
    
    # Run optimization
    optimizer = SequentialStageOptimizer(
        config=config,
        template_scenario_path=scenario_path,
        output_dir=output_dir,
        scenario_column=args.scenario_column
    )
    
    results = optimizer.optimize()
    
    # Return appropriate exit code
    if results.get('error'):
        print(f"\n❌ Optimization failed: {results.get('error')}")
        sys.exit(1)
    else:
        print(f"\n✅ Optimization complete!")
        print(f"Results saved to: {output_dir}")
        sys.exit(0)


if __name__ == "__main__":
    main()
