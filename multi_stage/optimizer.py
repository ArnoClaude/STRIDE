# multi_stage/optimizer.py

import subprocess
import os


class MultiStageOptimizer:
    def __init__(self, stages, base_scenario_path, settings_path):
        self.stages = stages  # [2025, 2030, 2035, 2040, 2045, 2050, 2055]
        self.base_scenario_path = base_scenario_path
        self.settings_path = settings_path
        self.results = {}

    def run_stage(self, stage_year, stage_idx):
        """Run REVOL-E-TION for a single stage"""

        # Generate stage-specific scenario file
        stage_scenario_path = self.generate_stage_scenario(
            year=stage_year,
            stage_idx=stage_idx,
            previous_results=self.results.get(stage_idx - 1, None)
        )

        # Call REVOL-E-TION via subprocess
        cmd = [
            'python3', '-m', 'revoletion.main',
            '--settings', self.settings_path,
            '--scenario', stage_scenario_path
        ]

        result = subprocess.run(
            cmd,
            cwd=os.path.join(os.path.dirname(__file__), '..', 'revoletion'),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Stage {stage_year} failed: {result.stderr}")

        # Parse results
        stage_results = self.parse_revoletion_output(stage_scenario_path)

        return stage_results