# multi_stage/sequential_optimizer.py

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class SequentialStageOptimizer:
    """
    Sequential multi-stage optimization wrapper for REVOL-E-TION.
    Optimizes each stage independently, passing capacities forward.
    """

    def __init__(
            self,
            stages: List[int] = [2025, 2030, 2035, 2040, 2045, 2050, 2055],
            base_scenario_path: str = "case_studies/baseline/scenario_template.csv",
            settings_path: str = "case_studies/baseline/settings.csv",
            output_dir: str = "results/multi_stage"
    ):
        self.stages = stages
        self.base_scenario_path = Path(base_scenario_path)
        self.settings_path = Path(settings_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Store results from each stage
        self.results = {}

    def optimize(self) -> Dict:
        """
        Run sequential optimization across all stages.

        Returns:
            Dictionary with results for each stage
        """
        print(f"\n{'=' * 60}")
        print(f"Starting Multi-Stage Sequential Optimization")
        print(f"Stages: {self.stages}")
        print(f"{'=' * 60}\n")

        for stage_idx, year in enumerate(self.stages):
            print(f"\n{'=' * 60}")
            print(f"STAGE {stage_idx + 1}/{len(self.stages)}: Year {year}")
            print(f"{'=' * 60}")

            # 1. Generate stage-specific scenario
            stage_scenario_path = self.generate_stage_scenario(
                year=year,
                stage_idx=stage_idx
            )

            # 2. Run REVOL-E-TION
            stage_results = self.run_revoletion_stage(
                scenario_path=stage_scenario_path,
                year=year
            )

            # 3. Store results
            self.results[year] = stage_results

            print(f"\nStage {year} completed successfully!")
            self.print_stage_summary(year, stage_results)

        # 4. Calculate overall NPV
        total_npv = self.calculate_multi_stage_npv()

        # 5. Save final results
        self.save_results()

        print(f"\n{'=' * 60}")
        print(f"Multi-Stage Optimization Complete!")
        print(f"Total NPV: ${total_npv:,.2f}")
        print(f"{'=' * 60}\n")

        return self.results

    def generate_stage_scenario(
            self,
            year: int,
            stage_idx: int
    ) -> Path:
        """
        Generate scenario CSV file for a specific stage.

        If stage_idx > 0, use previous stage's optimized capacities
        as 'size_existing' for this stage.
        """
        # Read base scenario template
        scenario_df = pd.read_csv(self.base_scenario_path)

        # If not first stage, update with previous capacities
        if stage_idx > 0:
            prev_year = self.stages[stage_idx - 1]
            prev_results = self.results[prev_year]

            # Update existing sizes from previous stage
            # Example: PV capacity
            if 'pv_size_total' in prev_results:
                pv_size = prev_results['pv_size_total']
                # Find row where block='pv' and key='size_existing'
                mask = (scenario_df['block'] == 'pv') & (scenario_df['key'] == 'size_existing')
                scenario_df.loc[mask, scenario_df.columns[2]] = pv_size  # Column 2 is scenario data

            # Similar for battery, grid, chargers...
            # (You'll expand this based on actual components)

        # Update scenario parameters for this stage
        # (e.g., future electricity prices, fleet size, etc.)

        # Save stage-specific scenario file
        stage_scenario_path = self.output_dir / f"scenario_stage_{year}.csv"
        scenario_df.to_csv(stage_scenario_path, index=False)

        print(f"Generated scenario file: {stage_scenario_path}")
        return stage_scenario_path

    def run_revoletion_stage(
            self,
            scenario_path: Path,
            year: int
    ) -> Dict:
        """
        Run REVOL-E-TION for a single stage.

        Returns:
            Dictionary with stage results
        """
        print(f"\nRunning REVOL-E-TION for year {year}...")

        # Build command
        revoletion_dir = Path(__file__).parent.parent / "revoletion"
        cmd = [
            'python3', '-m', 'revoletion.main',
            '--settings', str(self.settings_path.resolve()),
            '--scenario', str(scenario_path.resolve())
        ]

        # Run REVOL-E-TION
        result = subprocess.run(
            cmd,
            cwd=str(revoletion_dir),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"ERROR: REVOL-E-TION failed for year {year}")
            print(f"STDERR: {result.stderr}")
            raise RuntimeError(f"Stage {year} optimization failed")

        print(f"REVOL-E-TION completed for year {year}")

        # Parse results
        stage_results = self.parse_revoletion_output(scenario_path)

        return stage_results

    def parse_revoletion_output(
            self,
            scenario_path: Path
    ) -> Dict:
        """
        Parse REVOL-E-TION output files to extract results.

        Returns:
            Dictionary with parsed results
        """
        # REVOL-E-TION creates results in revoletion/results/
        # Find the most recent results directory
        results_base = Path(__file__).parent.parent / "revoletion" / "results"

        # Get most recent results directory
        result_dirs = sorted(results_base.glob("*"), key=os.path.getmtime, reverse=True)
        if not result_dirs:
            raise RuntimeError("No REVOL-E-TION results found")

        latest_results_dir = result_dirs[0]
        print(f"Parsing results from: {latest_results_dir}")

        # Parse summary CSV
        summary_files = list(latest_results_dir.glob("*_summary.csv"))
        if not summary_files:
            raise RuntimeError("No summary file found")

        summary_df = pd.read_csv(summary_files[0])

        # Extract key results
        results = {
            'results_dir': str(latest_results_dir),
            'npv': self._extract_value(summary_df, 'npv'),
            'npc': self._extract_value(summary_df, 'npc'),
            'lcoe': self._extract_value(summary_df, 'lcoe'),
        }

        # Extract component sizes
        component_sizes = {
            'pv_size_total': self._extract_value(summary_df, 'pv', 'size', 'total'),
            'ess_size_total': self._extract_value(summary_df, 'ess', 'size', 'total'),
            'grid_size_g2s_total': self._extract_value(summary_df, 'grid', 'size', 'g2s', 'total'),
        }

        results.update(component_sizes)

        return results

    def _extract_value(self, df: pd.DataFrame, *keys) -> Optional[float]:
        """Helper to extract values from summary DataFrame"""
        try:
            # This is a placeholder - actual extraction depends on
            # how REVOL-E-TION structures its summary CSV
            # You'll need to inspect the actual file format
            return 0.0  # Placeholder
        except:
            return None

    def print_stage_summary(self, year: int, results: Dict):
        """Print summary of stage results"""
        print(f"\nResults for Stage {year}:")
        print(f"  NPV: ${results.get('npv', 0):,.2f}")
        print(f"  NPC: ${results.get('npc', 0):,.2f}")
        print(f"  LCOE: ${results.get('lcoe', 0):.2f}/kWh")
        if results.get('pv_size_total'):
            print(f"  PV Capacity: {results['pv_size_total'] / 1000:.1f} kW")
        if results.get('ess_size_total'):
            print(f"  Battery Capacity: {results['ess_size_total'] / 1000:.1f} kWh")

    def calculate_multi_stage_npv(self) -> float:
        """
        Calculate total NPV across all stages.

        This is simplified - you'll need proper discounting
        """
        total_npv = sum(
            stage_results.get('npv', 0)
            for stage_results in self.results.values()
        )
        return total_npv

    def save_results(self):
        """Save final multi-stage results"""
        output_file = self.output_dir / "multi_stage_results.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\nResults saved to: {output_file}")


# Example usage
if __name__ == "__main__":
    optimizer = SequentialStageOptimizer(
        stages=[2025, 2030, 2035],  # Start with just 3 stages for testing
        base_scenario_path="../revoletion/example/scenarios_example.csv",
        settings_path="../revoletion/example/settings.csv"
    )

    results = optimizer.optimize()