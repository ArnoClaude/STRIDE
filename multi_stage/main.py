#!/usr/bin/env python3
"""
STRIDE - Sequential Temporal Resource Investment for Depot Electrification

Multi-stage optimization CLI entry point.

Usage:
    python -m multi_stage.main -c CONFIG [CONFIG ...] -s SCENARIO [--name NAME]

Example:
    python -m multi_stage.main \
        -c configs/base.yaml configs/depots/schmid.yaml \
        -s inputs/schmid/scenarios/base.csv \
        --name schmid_base
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="STRIDE: Multi-stage depot electrification optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schmid base run
  python -m multi_stage.main \\
      -c configs/base.yaml configs/depots/schmid.yaml \\
      -s inputs/schmid/scenarios/base.csv \\
      --name schmid_base

  # Schmid with optimistic scenario
  python -m multi_stage.main \\
      -c configs/base.yaml configs/depots/schmid.yaml configs/scenarios/optimistic.yaml \\
      -s inputs/schmid/scenarios/base.csv \\
      --name schmid_optimistic

  # Schmid with WACC sensitivity
  python -m multi_stage.main \\
      -c configs/base.yaml configs/depots/schmid.yaml configs/sensitivity/wacc_high.yaml \\
      -s inputs/schmid/scenarios/base.csv \\
      --name schmid_wacc_high
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        required=True,
        nargs="+",
        help="Path(s) to YAML config file(s). Multiple files are merged in order (base first, overrides last)"
    )
    
    parser.add_argument(
        "--scenario", "-s",
        required=True,
        help="Path to base scenario CSV template"
    )
    
    parser.add_argument(
        "--name", "-n",
        default=None,
        help="Run name (default: auto-generated from date, type, depot, scenario)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["base", "sensitivity", "debug", "test"],
        default="base",
        help="Run type for organization (default: base)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory (default: runs/<name>/). Deprecated: prefer --name"
    )
    
    parser.add_argument(
        "--scenario-column",
        default=None,
        help="Scenario column name to use from template (default: first column)"
    )
    
    args = parser.parse_args()
    
    # Validate paths
    config_paths = [Path(c).resolve() for c in args.config]
    scenario_path = Path(args.scenario).resolve()
    
    for config_path in config_paths:
        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}")
            sys.exit(1)
    
    if not scenario_path.exists():
        print(f"❌ Scenario file not found: {scenario_path}")
        sys.exit(1)
    
    # Import here to avoid slow startup for --help
    from .config_loader import MultiStageConfig
    from .sequential_optimizer import SequentialStageOptimizer
    from .manifest import ManifestGenerator, generate_run_name
    
    # Load config (chain multiple files)
    print(f"Loading configs: {[p.name for p in config_paths]}")
    config = MultiStageConfig.from_yaml_chain([str(p) for p in config_paths])
    
    # Determine run name
    if args.name:
        run_name = args.name
    else:
        run_name = generate_run_name(config_paths[-1], scenario_path, args.type)
    
    # Determine output directory
    repo_root = Path(__file__).parent.parent
    if args.output:
        # Legacy: explicit output path
        output_dir = Path(args.output).resolve()
    else:
        # New: runs/<name>/
        output_dir = repo_root / "runs" / run_name
    
    # Check if run already exists
    if output_dir.exists():
        # Add timestamp suffix to make unique
        timestamp = datetime.now().strftime("%H%M%S")
        run_name = f"{run_name}_{timestamp}"
        output_dir = repo_root / "runs" / run_name
        print(f"⚠️  Run directory exists, using: {run_name}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Reconstruct command for manifest
    config_args = " ".join([f"-c {c}" for c in args.config])
    command = f"python -m multi_stage.main {config_args} -s {args.scenario}"
    if args.name:
        command += f" --name {args.name}"
    if args.type != "base":
        command += f" --type {args.type}"
    
    # Copy input files to run directory for traceability
    print(f"\nCopying input files to run directory...")
    for i, cp in enumerate(config_paths):
        shutil.copy(cp, output_dir / f"config_{i}_{cp.name}")
    shutil.copy(scenario_path, output_dir / "scenario_template.csv")
    shutil.copy(config.revoletion_settings_path, output_dir / "settings_original.csv")
    
    # Copy timeseries directory for full reproducibility
    timeseries_src = scenario_path.parent / "timeseries"
    if not timeseries_src.exists():
        # Try parent's timeseries (for scenarios in subdirectory)
        timeseries_src = scenario_path.parent.parent / "timeseries"
    
    if timeseries_src.exists() and timeseries_src.is_dir():
        timeseries_dst = output_dir / "timeseries"
        shutil.copytree(timeseries_src, timeseries_dst)
        ts_count = len(list(timeseries_dst.glob("*.csv")))
        print(f"  ✓ Copied config.yaml, scenario_template.csv, settings_original.csv")
        print(f"  ✓ Copied timeseries/ ({ts_count} files)")
    else:
        print(f"  ✓ Copied config.yaml, scenario_template.csv, settings_original.csv")
        print(f"  ⚠ No timeseries directory found at {timeseries_src}")
    
    # Generate initial manifest
    manifest_gen = ManifestGenerator(
        run_name=run_name,
        run_type=args.type,
        config_path=config_paths,
        scenario_path=scenario_path,
        settings_path=config.revoletion_settings_path,
        output_dir=output_dir,
        command=command
    )
    manifest = manifest_gen.generate(config)
    manifest_path = manifest_gen.save(manifest)
    print(f"  ✓ Created manifest.yaml")
    
    # Print run summary
    print(f"\n{'='*60}")
    print(f"STRIDE Multi-Stage Optimization")
    print(f"{'='*60}")
    print(f"Run Name: {run_name}")
    print(f"Run Type: {args.type}")
    print(f"Configs:  {[p.name for p in config_paths]}")
    print(f"Scenario: {scenario_path.name}")
    print(f"Output:   {output_dir}")
    print(f"Stages:   {config.stages}")
    print(f"Fleet:    {config.demand_base_num_vehicles} vehicles (base)")
    print(f"Growth:   {config.demand_annual_growth_rate*100:.1f}%/yr")
    print(f"WACC:     {config.wacc*100:.1f}%")
    if manifest['git']['commit']:
        dirty = " (dirty)" if manifest['git']['dirty'] else ""
        print(f"Git:      {manifest['git']['commit']}{dirty}")
    print(f"{'='*60}\n")
    
    # Run optimization
    optimizer = SequentialStageOptimizer(
        config=config,
        template_scenario_path=scenario_path,
        output_dir=output_dir,
        scenario_column=args.scenario_column,
        run_name=run_name
    )
    
    results = optimizer.optimize()
    
    # Update manifest with results
    if results.get('error'):
        results_summary = {
            "status": "failed",
            "error": results.get('error'),
            "stages_completed": len(results.get('completed_stages', {})),
            "infeasible_year": results.get('infeasible_year'),
        }
    else:
        results_summary = {
            "status": "completed",
            "stages_completed": len(config.stages),
            "total_npv": results.get('total_npv'),
            "total_capex": results.get('total_capex'),
        }
    
    manifest_gen.update_results(manifest_path, results_summary)
    
    # Return appropriate exit code
    if results.get('error'):
        print(f"\n❌ Optimization failed: {results.get('error')}")
        sys.exit(1)
    else:
        print(f"\n✅ Optimization complete!")
        print(f"Run name: {run_name}")
        print(f"Results:  {output_dir}")
        print(f"Manifest: {manifest_path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
