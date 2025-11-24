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
        scenario_column: str = None,
        stage_duration: int = None
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
        stage_duration : int, optional
            Duration of this stage in years (e.g., 5 for 2025-2030)
            If not provided, uses template default (typically 25 years)

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

        # Extract only the selected scenario column (drop all other scenario columns)
        all_columns = scenario_df.columns.tolist()
        data_columns = [col for col in all_columns if col not in ['block', 'key']]
        columns_to_drop = [col for col in data_columns if col != scenario_column]
        scenario_df = scenario_df.drop(columns=columns_to_drop)

        print(f"  - Using scenario column: '{scenario_column}'")

        # Print CO2 constraint if present
        co2_mask = (scenario_df['block'] == 'scenario') & (scenario_df['key'] == 'co2_max')
        if co2_mask.any():
            co2_value = scenario_df.loc[co2_mask, scenario_column].values[0]
            if pd.notna(co2_value) and co2_value != '' and co2_value != 'None':
                print(f"  - CO2 limit: {co2_value} kg")

        # Update project duration for this stage
        if stage_duration is not None:
            prj_mask = (scenario_df['block'] == 'scenario') & (scenario_df['key'] == 'prj_duration')
            if prj_mask.any():
                scenario_df.loc[prj_mask, scenario_column] = stage_duration
                print(f"  - Stage duration: {stage_duration} years")

        # 1. Apply stage-linking constraints (if not first stage)
        if previous_stage_results is not None:
            scenario_df = self._apply_stage_linking(
                scenario_df,
                previous_stage_results,
                scenario_column
            )

        # 2. Update costs for this stage year (technology learning curves)
        scenario_df = self._update_costs(scenario_df, stage_year, scenario_column)

        # 3. Update demand/fleet size (growth trajectory)
        scenario_df = self._update_demand(scenario_df, stage_year, scenario_column)

        # 4. Update CO2 limits (decarbonization pathway)
        scenario_df = self._update_co2_limits(scenario_df, stage_year, scenario_column)

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

        Implements exponential cost decline curves:
        - PV: 5% annual decline
        - ESS: 8% annual decline
        """
        base_year = 2025
        years_elapsed = stage_year - base_year

        if years_elapsed > 0:
            # PV: 5% annual decline
            pv_decline_rate = 0.05
            pv_mask = (df['block'] == 'pv') & (df['key'] == 'capex_spec')
            if pv_mask.any():
                pv_cost_base = df.loc[pv_mask, column].values[0]
                if pd.notna(pv_cost_base) and pv_cost_base != '' and pv_cost_base != 'None':
                    pv_cost_base = float(pv_cost_base)
                    pv_cost_new = pv_cost_base * ((1 - pv_decline_rate) ** years_elapsed)
                    df.loc[pv_mask, column] = pv_cost_new
                    print(f"  - PV cost: ${pv_cost_base:.2f}/W → ${pv_cost_new:.2f}/W ({-pv_decline_rate*100:.0f}%/yr)")

            # ESS: 8% annual decline
            ess_decline_rate = 0.08
            ess_mask = (df['block'] == 'ess') & (df['key'] == 'capex_spec')
            if ess_mask.any():
                ess_cost_base = df.loc[ess_mask, column].values[0]
                if pd.notna(ess_cost_base) and ess_cost_base != '' and ess_cost_base != 'None':
                    ess_cost_base = float(ess_cost_base)
                    ess_cost_new = ess_cost_base * ((1 - ess_decline_rate) ** years_elapsed)
                    df.loc[ess_mask, column] = ess_cost_new
                    print(f"  - ESS cost: ${ess_cost_base:.3f}/Wh → ${ess_cost_new:.3f}/Wh ({-ess_decline_rate*100:.0f}%/yr)")

        return df

    def _update_demand(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update demand/fleet size based on growth projections.

        Implements 10% annual fleet growth:
        - Scales demand profile proportionally
        - Updates fleet size (number of vehicles)
        - Updates annual consumption
        """
        base_year = 2025
        years_elapsed = stage_year - base_year

        if years_elapsed > 0:
            growth_rate = 0.10  # 10% annual growth
            growth_factor = (1 + growth_rate) ** years_elapsed

            # Update fleet size (number of vehicles)
            fleet_mask = (df['block'] == 'bev') & (df['key'] == 'size_existing')
            if fleet_mask.any():
                fleet_base = df.loc[fleet_mask, column].values[0]
                if pd.notna(fleet_base) and fleet_base != '' and fleet_base != 'None':
                    fleet_base = float(fleet_base)
                    fleet_new = fleet_base * growth_factor
                    df.loc[fleet_mask, column] = fleet_new
                    print(f"  - Fleet size: {fleet_base:.0f} vehicles → {fleet_new:.0f} vehicles (+{growth_rate*100:.0f}%/yr)")

            # Update annual consumption (scales with fleet)
            # NOTE: consumption_yrl is in 'dem' block, not 'bev' block
            consumption_mask = (df['block'] == 'dem') & (df['key'] == 'consumption_yrl')
            if consumption_mask.any():
                consumption_base = df.loc[consumption_mask, column].values[0]
                if pd.notna(consumption_base) and consumption_base != '' and consumption_base != 'None':
                    consumption_base = float(consumption_base)
                    consumption_new = consumption_base * growth_factor
                    df.loc[consumption_mask, column] = consumption_new
                    print(f"  - Annual consumption: {consumption_base/1e6:.1f} MWh → {consumption_new/1e6:.1f} MWh")

        return df

    def _update_co2_limits(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update CO2 limits based on decarbonization pathway.

        Implements linear tightening from 500 kg (2025) to 100 kg (2050).
        Always applies the pathway, including for base year.
        """
        base_year = 2025
        target_year = 2050
        years_elapsed = stage_year - base_year

        # Linear decarbonization pathway (applies to ALL years including base)
        co2_start = 500  # kg for 50-day simulation period
        co2_end = 100    # kg for 50-day simulation period
        co2_slope = (co2_end - co2_start) / (target_year - base_year)
        co2_limit_new = co2_start + co2_slope * years_elapsed

        # Update CO2 limit
        co2_mask = (df['block'] == 'scenario') & (df['key'] == 'co2_max')
        if co2_mask.any():
            co2_limit_base = df.loc[co2_mask, column].values[0]
            if pd.notna(co2_limit_base) and co2_limit_base != '' and co2_limit_base != 'None':
                co2_limit_base = float(co2_limit_base)
                df.loc[co2_mask, column] = co2_limit_new
                if years_elapsed > 0:
                    print(f"  - CO2 limit: {co2_limit_base:.0f} kg → {co2_limit_new:.0f} kg (decarbonization pathway)")
                else:
                    print(f"  - CO2 limit: {co2_limit_base:.0f} kg → {co2_limit_new:.0f} kg (pathway baseline)")

        return df

    def extract_scenario_column_names(self) -> list:
        """
        Get list of scenario column names from template.

        Returns:
        --------
        list : Column names (excluding 'block' and 'key')
        """
        return [col for col in self.template.columns if col not in ['block', 'key']]
