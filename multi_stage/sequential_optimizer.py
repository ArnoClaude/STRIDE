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
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .scenario_builder import ScenarioBuilder
from .results_parser import ResultsParser


class SequentialStageOptimizer:
    """
    Sequential multi-stage optimization wrapper for REVOL-E-TION.

    Runs optimization for each stage independently, feeding investment
    decisions forward as constraints for subsequent stages.
    """

    def __init__(
        self,
        stages: List[int],
        template_scenario_path: Path,
        settings_path: Path,
        revoletion_dir: Path,
        output_dir: Path,
        scenario_column: str = None,
        discount_rate: float = 0.09
    ):
        """
        Parameters:
        -----------
        stages : list of int
            Years to optimize (e.g., [2025, 2030, 2035, 2040, 2045, 2050])
        template_scenario_path : Path
            Base scenario CSV template
        settings_path : Path
            REVOL-E-TION settings CSV
        revoletion_dir : Path
            Directory containing REVOL-E-TION installation
        output_dir : Path
            Directory for saving results
        scenario_column : str, optional
            Which column from template to use (default: first scenario column)
        discount_rate : float
            WACC for NPV discounting (default: 0.09)
        """
        self.stages = stages
        self.template_scenario_path = template_scenario_path
        self.settings_path = settings_path
        self.revoletion_dir = revoletion_dir
        self.output_dir = output_dir
        self.scenario_column = scenario_column
        self.discount_rate = discount_rate

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize helper classes
        self.scenario_builder = ScenarioBuilder(template_scenario_path)
        self.results_parser = ResultsParser()

        # Storage for stage results
        self.stage_results = {}

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
        print(f"Stages: {self.stages}")
        print(f"Discount rate (WACC): {self.discount_rate:.1%}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*80}\n")

        # Run each stage sequentially
        for stage_idx, year in enumerate(self.stages):
            print(f"\n{'='*80}")
            print(f"STAGE {stage_idx + 1}/{len(self.stages)}: Year {year}")
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
                    stage_year=year,
                    discount_rate=self.discount_rate
                )

                # 4. Store results for next stage
                self.stage_results[year] = stage_result

                # 5. Print summary
                self._print_stage_summary(year, stage_result)

                # 6. Stop if infeasible (can't continue to next stage)
                if stage_result.get('status') == 'infeasible':
                    print(f"\n❌ Multi-stage optimization STOPPED due to infeasible stage {year}")
                    print(f"   Suggestion: Relax constraints (e.g., increase CO2 limit) or check scenario setup")
                    return {'error': 'infeasible_stage', 'completed_stages': self.stage_results}

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
            prev_year = self.stages[stage_idx - 1]
            previous_results = self.stage_results[prev_year]
            print(f"  - Inheriting capacities from year {prev_year}")

        # Create stage scenario
        output_path = self.output_dir / f"scenario_stage_{year}.csv"
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
        Path : Results directory
        """
        print(f"\n2. Running REVOL-E-TION optimization")

        # Build command
        cmd = [
            sys.executable,  # Use current Python interpreter (from venv)
            '-m', 'revoletion.main',
            '--settings', str(self.settings_path.absolute()),
            '--scenario', str(scenario_path.absolute())
        ]

        print(f"  - Command: {' '.join(cmd)}")
        print(f"  - Working dir: {self.revoletion_dir}")

        # Run optimization
        result = subprocess.run(
            cmd,
            cwd=str(self.revoletion_dir),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode != 0:
            print(f"\n❌ REVOL-E-TION failed!")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            raise RuntimeError(f"REVOL-E-TION optimization failed for year {year}")

        print(f"  ✓ REVOL-E-TION completed successfully")

        # Find results directory
        results_base = self.revoletion_dir / "results"
        result_dir = self.results_parser.get_latest_result_dir(results_base)

        print(f"  ✓ Results directory: {result_dir.name}")

        return result_dir

    def _print_stage_summary(self, year: int, results: Dict):
        """Print summary of stage results."""
        print(f"\n3. Stage {year} Results:")
        print(f"  ├─ Status: {results.get('status', 'unknown')}")

        # Handle infeasible scenarios
        if results.get('status') == 'infeasible':
            print(f"  └─ ⚠️  INFEASIBLE - No solution found (constraints too tight)")
            return

        print(f"  ├─ NPV: ${results.get('npv', 0):,.0f}")
        print(f"  ├─ NPV (discounted): ${results.get('npv_discounted', 0):,.0f}")
        print(f"  ├─ CAPEX: ${results.get('capex_prj', 0):,.0f}")
        print(f"  ├─ OPEX: ${results.get('opex_prj', 0):,.0f}")

        pv = results.get('pv_size_total', 0) or 0
        ess = results.get('ess_size_total', 0) or 0
        grid = results.get('grid_size_g2s', 0) or 0

        if pv:
            print(f"  ├─ PV total: {pv/1000:.1f} kW")
            pv_new = results.get('pv_size_invest', 0) or 0
            if pv_new:
                print(f"  │  └─ New: {pv_new/1000:.1f} kW")

        if ess:
            print(f"  ├─ Battery total: {ess/1000:.1f} kWh")
            ess_new = results.get('ess_size_invest', 0) or 0
            if ess_new:
                print(f"  │  └─ New: {ess_new/1000:.1f} kWh")

        if grid:
            print(f"  └─ Grid g2s: {grid/1000:.1f} kW")

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
