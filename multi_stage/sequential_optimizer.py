"""
Sequential Multi-Stage Optimizer for STRIDE.

Orchestrates multi-stage optimization by:
1. Running REVOL-E-TION for each stage sequentially
2. Passing investment decisions forward (stage linking)
3. Aggregating multi-stage NPV

Author: Arno Claude
Thesis: STRIDE - Sequential Temporal Resource Investment for Depot Electrification
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from .config_loader import MultiStageConfig
from .scenario_builder import ScenarioBuilder
from .results_parser import ResultsParser
from .utils import get_unit


class SequentialStageOptimizer:
    """
    Sequential multi-stage optimization wrapper for REVOL-E-TION.

    Runs optimization for each stage independently, feeding investment
    decisions forward as constraints for subsequent stages.

    Config-driven implementation - all parameters from MultiStageConfig.
    """

    def __init__(
        self,
        config: MultiStageConfig,
        template_scenario_path: Path,
        output_dir: Path,
        scenario_column: str = None,
        run_name: str = None
    ):
        """
        Parameters:
        -----------
        config : MultiStageConfig
            Configuration object with all optimization parameters
        template_scenario_path : Path
            Base scenario CSV template
        output_dir : Path
            Directory for saving results
        scenario_column : str, optional
            Which column from template to use (default: first scenario column)
        run_name : str, optional
            Name of this run (for logging/display)
        """
        self.config = config
        self.template_scenario_path = template_scenario_path
        self.output_dir = Path(output_dir).resolve()
        self.scenario_column = scenario_column
        self.run_name = run_name or output_dir.name

        # Override config paths - all outputs go inside the run directory
        self.config.stage_scenarios_dir = self.output_dir / "stages"
        self.config.summary_output_dir = self.output_dir
        
        # REVOL-E-TION outputs will go here (contained within run directory)
        self.revoletion_output_dir = self.output_dir / "revoletion"

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.stage_scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.revoletion_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create per-run settings.csv that points to our contained output directory
        self.run_settings_path = self._create_run_settings()

        # Initialize helper classes (config-driven)
        self.scenario_builder = ScenarioBuilder(template_scenario_path, config)
        self.results_parser = ResultsParser(config)

        # Storage for stage results (explicit tracking - no get_latest_result_dir)
        self.stage_results = {}

        # Validate setup before running
        self._validate_setup()

    def _validate_setup(self):
        """Pre-run validation to catch configuration errors early."""
        # Check template exists
        if not self.template_scenario_path.exists():
            raise FileNotFoundError(f"Template scenario not found: {self.template_scenario_path}")

        # Check settings file exists
        if not self.config.revoletion_settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {self.config.revoletion_settings_path}")

        # Config validation already done in MultiStageConfig.validate()
        # ScenarioBuilder._validate_template() checks required blocks exist

        print(f"✓ Setup validation passed")

    def _create_run_settings(self) -> Path:
        """
        Create a per-run settings.csv that directs REVOL-E-TION outputs
        into the run directory.
        
        This solves the scattered output problem - REVOL-E-TION will now
        save its timestamped folders inside runs/<name>/revoletion/
        
        Returns:
        --------
        Path : Path to generated settings.csv
        """
        # Read original settings
        settings_df = pd.read_csv(self.config.revoletion_settings_path)
        
        # Update path_output_data to point to our contained directory
        output_mask = settings_df['key'] == 'path_output_data'
        if output_mask.any():
            settings_df.loc[output_mask, 'value'] = str(self.revoletion_output_dir)
        else:
            # Add the row if it doesn't exist
            new_row = pd.DataFrame({'key': ['path_output_data'], 'value': [str(self.revoletion_output_dir)]})
            settings_df = pd.concat([settings_df, new_row], ignore_index=True)
        
        # Also update path_input_data to be absolute (in case relative path breaks)
        input_mask = settings_df['key'] == 'path_input_data'
        if input_mask.any():
            original_input_path = settings_df.loc[input_mask, 'value'].values[0]
            # Resolve relative to original settings location
            if not Path(original_input_path).is_absolute():
                resolved_input = (self.config.revoletion_settings_path.parent / original_input_path).resolve()
                settings_df.loc[input_mask, 'value'] = str(resolved_input)
        
        # Save to run directory
        run_settings_path = self.output_dir / "settings.csv"
        settings_df.to_csv(run_settings_path, index=False)
        
        print(f"  ✓ Created run-specific settings.csv")
        print(f"    REVOL-E-TION outputs → {self.revoletion_output_dir}")
        
        return run_settings_path

    def optimize(self) -> Dict:
        """
        Run sequential optimization across all stages.

        Returns:
        --------
        dict : Aggregated multi-stage results
        """
        print(f"\n{'='*80}")
        print(f"STRIDE Sequential Multi-Stage Optimization")
        print(f"{'='*80}")
        print(f"Stages: {self.config.stages}")
        print(f"Discount rate (WACC): {self.config.wacc:.1%}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*80}\n")

        # Run each stage sequentially
        for stage_idx, year in enumerate(self.config.stages):
            print(f"\n{'='*80}")
            print(f"STAGE {stage_idx + 1}/{len(self.config.stages)}: Year {year}")
            print(f"{'='*80}")

            try:
                # 1. Build scenario for this stage
                stage_scenario_path = self._generate_stage_scenario(
                    year=year,
                    stage_idx=stage_idx
                )

                # 2. Run REVOL-E-TION optimization
                result_dir = self._run_revoletion(
                    scenario_path=stage_scenario_path,
                    year=year
                )

                # 3. Parse results
                stage_result = self.results_parser.parse_stage_results(
                    result_dir=result_dir,
                    stage_year=year
                )

                # 4. Store results for next stage (explicit - no fragile detection)
                self.stage_results[year] = stage_result

                # 5. Print summary
                self._print_stage_summary(year, stage_result)
                
                # 6. Print trajectory across all completed stages
                self._print_trajectory_summary()

                # 7. Stop if infeasible (can't continue to next stage)
                if stage_result.get('status') == 'infeasible':
                    self._print_infeasibility_diagnostic(year)
                    return {
                        'error': 'infeasible_stage',
                        'infeasible_year': year,
                        'completed_stages': self.stage_results,
                        'total_stages': len(self.config.stages)
                    }

            except subprocess.TimeoutExpired as e:
                print(f"\n❌ ERROR: Stage {year} timed out after {e.timeout}s")
                raise
            except Exception as e:
                print(f"\n❌ ERROR in stage {year}: {e}")
                raise

        # Aggregate results across all stages
        aggregated = self.results_parser.aggregate_multi_stage_results(
            self.stage_results
        )

        # Save final results
        self._save_results(aggregated)

        # Print final summary
        self._print_final_summary(aggregated)

        return aggregated

    def _generate_stage_scenario(self, year: int, stage_idx: int) -> Path:
        """
        Generate scenario CSV for a specific stage.

        Parameters:
        -----------
        year : int
            Stage year
        stage_idx : int
            Index in stages list (0-based)

        Returns:
        --------
        Path : Generated scenario file path
        """
        print(f"\n1. Generating scenario for year {year}")

        # Get previous stage results (if not first stage)
        previous_results = None
        if stage_idx > 0:
            prev_year = self.config.stages[stage_idx - 1]
            previous_results = self.stage_results[prev_year]

        # Create stage scenario (stage_duration comes from config, not calculated)
        output_path = self.config.stage_scenarios_dir / f"scenario_stage_{year}.csv"
        self.scenario_builder.create_stage_scenario(
            stage_year=year,
            output_path=output_path,
            previous_stage_results=previous_results,
            scenario_column=self.scenario_column
        )

        return output_path

    def _run_revoletion(self, scenario_path: Path, year: int) -> Path:
        """
        Run REVOL-E-TION optimization.

        Parameters:
        -----------
        scenario_path : Path
            Scenario file for this stage
        year : int
            Stage year

        Returns:
        --------
        Path : Results directory (explicit - no guessing!)
        """
        print(f"\n2. Running REVOL-E-TION optimization")

        # Build command - use our run-specific settings.csv
        cmd = [
            sys.executable,  # Use current Python interpreter (from venv)
            '-m', 'revoletion.main',
            '--settings', str(self.run_settings_path.absolute()),
            '--scenario', str(scenario_path.absolute())
        ]

        # Working directory should be repo root for revoletion imports to work
        working_dir = Path(__file__).parent.parent

        print(f"  - Command: python -m revoletion.main ...")
        print(f"  - Settings: {self.run_settings_path.name}")
        print(f"  - Scenario: {scenario_path.name}")

        # Run optimization
        # Timeout: 60 minutes per stage (scaled fleets with 100+ vehicles take longer)
        result = subprocess.run(
            cmd,
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=3600  # 60 minute timeout
        )

        if result.returncode != 0:
            print(f"\n❌ REVOL-E-TION failed!")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            raise RuntimeError(f"REVOL-E-TION optimization failed for year {year}")

        # Check stdout for debug messages (CO2 constraint, etc.)
        if "DEBUG" in result.stdout:
            print(f"\n  Debug output:")
            for line in result.stdout.split('\n'):
                if "DEBUG" in line or (line.strip().startswith('-') and 'CO2' in line):
                    print(f"    {line}")

        print(f"  ✓ REVOL-E-TION completed successfully")

        # Find results directory - now contained in our revoletion/ folder
        result_dir = self.results_parser.get_latest_result_dir(
            self.revoletion_output_dir
        )

        print(f"  ✓ Results: revoletion/{result_dir.name}")

        return result_dir

    def _print_stage_summary(self, year: int, results: Dict):
        """Print summary of stage results (generic - shows ALL investable blocks)."""
        print(f"\n3. Stage {year} Results:")

        # Handle infeasible scenarios
        if results.get('status') == 'infeasible':
            print(f"  ├─ Status: ❌ INFEASIBLE")
            print(f"  └─ ⚠️  No solution found - constraints too tight!")
            return

        print(f"  ├─ Status: ✓ {results.get('status', 'unknown')}")

        print(f"  ├─ NPV: ${results.get('npv') or 0:,.0f}")
        print(f"  ├─ NPV (discounted): ${results.get('npv_discounted') or 0:,.0f}")
        print(f"  ├─ CAPEX: ${results.get('capex_prj') or 0:,.0f}")
        print(f"  ├─ OPEX: ${results.get('opex_prj') or 0:,.0f}")

        # Generic investment display - loop over ALL investable blocks from config
        print(f"  ├─ Investments:")

        for block_cfg in self.config.investable_blocks:
            total = results.get(f'{block_cfg.name}_size_total', 0) or 0
            new = results.get(f'{block_cfg.name}_size_invest', 0) or 0

            if total > 0:
                unit = get_unit(block_cfg.name)
                if unit in ['kW', 'kWh', 'kWp']:
                    print(f"  │  ├─ {block_cfg.name}: {total/1000:.1f} {unit} total")
                    if new > 0:
                        print(f"  │  │  └─ New: {new/1000:.1f} {unit}")
                elif unit == 'vehicles':
                    print(f"  │  ├─ {block_cfg.name}: {int(total):,} {unit} total")
                    if new > 0:
                        print(f"  │  │  └─ New: {int(new):,} {unit}")
                else:
                    print(f"  │  ├─ {block_cfg.name}: {total:.0f} {unit} total")
                    if new > 0:
                        print(f"  │  │  └─ New: {new:.0f} {unit}")

        # Special display for grid g2s (if not already shown by investable_blocks loop)
        grid_g2s = results.get('grid_size_g2s', 0) or 0
        if grid_g2s > 0 and 'grid' not in [b.name for b in self.config.investable_blocks]:
            print(f"  └─ Grid g2s: {grid_g2s/1000:.1f} kW")

    def _print_trajectory_summary(self):
        """
        Print trajectory of key metrics across ALL completed stages.
        
        Shows absolute values and percentage changes between consecutive stages
        for each metric that changes over time.
        """
        if len(self.stage_results) < 1:
            return  # Need at least 1 stage to show anything
        
        years = sorted(self.stage_results.keys())
        
        print(f"\n{'─'*80}")
        if len(years) == 1:
            print(f"TRAJECTORY: Stage {years[0]} (baseline)")
        else:
            print(f"TRAJECTORY: Stages {years[0]} → {years[-1]}")
        print(f"{'─'*80}")
        
        # Define metrics to track with display formatting
        metrics = [
            ('pv_size_total', 'PV (kWp)', 'kW', 1000),
            ('ess_size_total', 'ESS (kWh)', 'kWh', 1000),
            ('grid_size_g2s', 'Grid (kW)', 'kW', 1000),
            ('npv_discounted', 'NPV (€)', '€', 1),
            ('capex_prj', 'CAPEX (€)', '€', 1),
            ('co2_sim_kg', 'CO2 (kg)', 'kg', 1),
        ]
        
        # Build header row
        header = f"{'Metric':<15}"
        for year in years:
            header += f" │ {year:>10}"
        print(header)
        print(f"{'─'*15}" + "─┼───────────" * len(years))
        
        # Print each metric row
        for key, label, unit, divisor in metrics:
            # Skip if no data for this metric
            if not any(self.stage_results[y].get(key) for y in years):
                continue
            
            row = f"{label:<15}"
            prev_val = None
            
            for year in years:
                val = self.stage_results[year].get(key, 0) or 0
                display_val = val / divisor
                
                if unit == '€':
                    cell = f"{display_val:>10,.0f}"
                elif unit in ['kW', 'kWh']:
                    cell = f"{display_val:>10.1f}"
                else:
                    cell = f"{display_val:>10,.0f}"
                
                row += f" │ {cell}"
                prev_val = val
            
            print(row)
        
        # Print percentage changes row for key capacity metrics
        print(f"{'─'*15}" + "─┼───────────" * len(years))
        print(f"{'Δ% vs prev':<15}", end="")
        
        for i, year in enumerate(years):
            if i == 0:
                print(f" │ {'─':>10}", end="")
            else:
                prev_year = years[i-1]
                # Use PV as representative metric for % change
                curr_pv = self.stage_results[year].get('pv_size_total', 0) or 0
                prev_pv = self.stage_results[prev_year].get('pv_size_total', 0) or 0
                
                if prev_pv > 0:
                    pct_change = (curr_pv - prev_pv) / prev_pv * 100
                    print(f" │ {pct_change:>+9.1f}%", end="")
                elif curr_pv > 0:
                    print(f" │ {'new':>10}", end="")
                else:
                    print(f" │ {'─':>10}", end="")
        print()
        print(f"{'─'*80}\n")

    def _print_infeasibility_diagnostic(self, year: int):
        """Print diagnostic information for infeasible stage."""
        print(f"\n{'='*80}")
        print(f"❌ MULTI-STAGE OPTIMIZATION STOPPED - INFEASIBLE STAGE")
        print(f"{'='*80}")
        print(f"Stage {year} was INFEASIBLE - no solution found.")
        print(f"\nPossible causes:")
        print(f"  • CO2 constraint too tight for available technologies")
        print(f"  • Insufficient capacity inherited from previous stage")
        print(f"  • Conflicting constraints (e.g., demand > max grid + PV + ESS)")
        print(f"\nSuggestions:")

        # Config-driven suggestions
        co2_limit = self.config.calculate_co2_limit(year)
        print(f"  • Increase CO2 limit (current: {co2_limit:.0f} kg)")
        print(f"  • Reduce fleet growth rate (current: {self.config.demand_annual_growth_rate*100:.0f}%/yr)")
        print(f"  • Relax technology cost constraints")
        print(f"  • Check scenario constraints in template CSV")

        print(f"\nCompleted stages: {list(self.stage_results.keys())}")
        print(f"{'='*80}\n")

    def _print_final_summary(self, aggregated: Dict):
        """Print final multi-stage summary."""
        print(f"\n{'='*80}")
        print(f"MULTI-STAGE OPTIMIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total NPV (discounted): ${aggregated['total_npv']:,.0f}")
        print(f"Total CAPEX: ${aggregated['total_capex']:,.0f}")
        print(f"\nInvestment Timeline:")

        timeline = aggregated['investment_timeline']
        for _, row in timeline.iterrows():
            print(f"  {int(row['year'])}: "
                  f"PV {row['pv_new_kw']:.0f} kW, "
                  f"ESS {row['ess_new_kwh']:.0f} kWh, "
                  f"CAPEX ${row['capex']:,.0f}")

        print(f"{'='*80}\n")

    def _save_results(self, aggregated: Dict):
        """Save aggregated results to JSON and CSV."""
        # Save full results as JSON
        json_path = self.output_dir / "multi_stage_results.json"
        with open(json_path, 'w') as f:
            json.dump(aggregated['stage_results'], f, indent=2, default=str)
        print(f"\n✓ Results saved to: {json_path}")

        # Save investment timeline as CSV
        csv_path = self.output_dir / "investment_timeline.csv"
        aggregated['investment_timeline'].to_csv(csv_path, index=False)
        print(f"✓ Timeline saved to: {csv_path}")
