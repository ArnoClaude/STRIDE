"""
Scenario Builder for multi-stage optimization.

Generates stage-specific scenario CSV files with:
- Updated existing capacities (from previous stage)
- Technology costs (for this stage year)
- Demand projections (for this stage year)
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd


class ScenarioBuilder:
    """
    Build scenario CSV files for each stage of multi-stage optimization.
    """

    def __init__(self, template_path: Path):
        """
        Parameters:
        -----------
        template_path : Path
            Path to base scenario CSV template
        """
        self.template_path = template_path
        self.template = pd.read_csv(template_path)

    def create_stage_scenario(
        self,
        stage_year: int,
        output_path: Path,
        previous_stage_results: Optional[Dict] = None,
        scenario_column: str = None
    ) -> Path:
        """
        Create scenario CSV for a specific stage.

        Parameters:
        -----------
        stage_year : int
            Year of this stage (e.g., 2025, 2030)
        output_path : Path
            Where to save the generated scenario file
        previous_stage_results : dict, optional
            Results from previous stage (for stage linking)
        scenario_column : str, optional
            Name of scenario column in template to use

        Returns:
        --------
        Path : Path to created scenario file
        """
        # Copy template
        scenario_df = self.template.copy()

        # Determine which column to use (default to 3rd column after block/key)
        if scenario_column is None:
            # Use first scenario column (usually column index 2)
            data_columns = [col for col in scenario_df.columns if col not in ['block', 'key']]
            if not data_columns:
                raise ValueError("No scenario columns found in template")
            scenario_column = data_columns[0]

        # 1. Apply stage-linking constraints (if not first stage)
        if previous_stage_results is not None:
            scenario_df = self._apply_stage_linking(
                scenario_df,
                previous_stage_results,
                scenario_column
            )

        # 2. Update costs for this stage year (future work - cost curves)
        # scenario_df = self._update_costs(scenario_df, stage_year, scenario_column)

        # 3. Update demand/fleet size (future work)
        # scenario_df = self._update_demand(scenario_df, stage_year, scenario_column)

        # Save to output path
        scenario_df.to_csv(output_path, index=False)
        print(f"  ✓ Created scenario file: {output_path.name}")

        return output_path

    def _apply_stage_linking(
        self,
        df: pd.DataFrame,
        prev_results: Dict,
        column: str
    ) -> pd.DataFrame:
        """
        Apply stage-linking constraints from previous stage results.

        This sets 'size_existing' for each component to the total
        capacity from the previous stage.

        Parameters:
        -----------
        df : DataFrame
            Scenario template
        prev_results : dict
            Previous stage results
        column : str
            Column name to update

        Returns:
        --------
        DataFrame : Updated scenario
        """
        # PV: Previous total becomes existing
        if 'pv_size_total' in prev_results and prev_results['pv_size_total'] is not None:
            pv_size = prev_results['pv_size_total']  # in W
            mask = (df['block'] == 'pv') & (df['key'] == 'size_existing')
            df.loc[mask, column] = pv_size
            print(f"  - PV existing: {pv_size/1000:.1f} kW (from previous stage)")

        # ESS (battery): Previous total becomes existing
        if 'ess_size_total' in prev_results and prev_results['ess_size_total'] is not None:
            ess_size = prev_results['ess_size_total']  # in Wh
            mask = (df['block'] == 'ess') & (df['key'] == 'size_existing')
            df.loc[mask, column] = ess_size
            print(f"  - ESS existing: {ess_size/1000:.1f} kWh (from previous stage)")

        # Grid connection (g2s = grid-to-system)
        if 'grid_size_g2s' in prev_results and prev_results['grid_size_g2s'] is not None:
            grid_g2s = prev_results['grid_size_g2s']  # in W
            mask = (df['block'] == 'grid') & (df['key'] == 'size_g2s_existing')
            df.loc[mask, column] = grid_g2s
            print(f"  - Grid g2s existing: {grid_g2s/1000:.1f} kW (from previous stage)")

        # Grid connection (s2g = system-to-grid, for export)
        if 'grid_size_s2g' in prev_results and prev_results['grid_size_s2g'] is not None:
            grid_s2g = prev_results['grid_size_s2g']  # in W
            mask = (df['block'] == 'grid') & (df['key'] == 'size_s2g_existing')
            df.loc[mask, column] = grid_s2g
            print(f"  - Grid s2g existing: {grid_s2g/1000:.1f} kW (from previous stage)")

        # Note: For BEV chargers, existing fleet typically stays
        # You might want to add fleet growth logic here

        return df

    def _update_costs(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update technology costs based on stage year.

        Placeholder for future cost curve implementation.
        """
        # TODO: Implement cost curves
        # - PV capex_spec declining over time
        # - ESS capex_spec declining over time
        # - Charger costs
        return df

    def _update_demand(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update demand/fleet size based on growth projections.

        Placeholder for future demand evolution implementation.
        """
        # TODO: Implement fleet growth
        # - Scale demand profile
        # - Increase number of vehicles
        # - Update consumption_yrl
        return df

    def extract_scenario_column_names(self) -> list:
        """
        Get list of scenario column names from template.

        Returns:
        --------
        list : Column names (excluding 'block' and 'key')
        """
        return [col for col in self.template.columns if col not in ['block', 'key']]
