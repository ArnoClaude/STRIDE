"""
Scenario Builder for multi-stage optimization.

Generates stage-specific scenario CSV files with:
- Updated existing capacities (from previous stage)
- Technology costs (for this stage year)
- Demand projections (for this stage year)
- CO2 limits (decarbonization pathway)
- Scaled bev_log files for fleet growth
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd

from .config_loader import MultiStageConfig
from .fleet_scaler import scale_bev_log
from .utils import get_unit


class ScenarioBuilder:
    """
    Build scenario CSV files for each stage of multi-stage optimization.
    Config-driven implementation - no hardcoded parameters.
    """

    def __init__(self, template_path: Path, config: MultiStageConfig):
        """
        Parameters:
        -----------
        template_path : Path
            Path to base scenario CSV template
        config : MultiStageConfig
            Configuration object with all parameters
        """
        self.template_path = template_path
        self.template = pd.read_csv(template_path)
        self.config = config

        # Validate template has required blocks
        self._validate_template()

    def _validate_template(self):
        """Check that template CSV contains all required blocks."""
        existing_blocks = set(self.template['block'].unique())

        # Check investable blocks
        for block_cfg in self.config.investable_blocks:
            if block_cfg.name not in existing_blocks:
                raise ValueError(f"Required investable block '{block_cfg.name}' "
                               f"not found in template. Available: {existing_blocks}")

        # Check demand blocks
        for block_cfg in self.config.demand_blocks:
            if block_cfg.name not in existing_blocks:
                raise ValueError(f"Required demand block '{block_cfg.name}' "
                               f"not found in template. Available: {existing_blocks}")

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

        # Determine which column to use
        if scenario_column is None:
            data_columns = [col for col in scenario_df.columns
                          if col not in ['block', 'key']]
            if not data_columns:
                raise ValueError("No scenario columns found in template")
            scenario_column = data_columns[0]

        # Extract only the selected scenario column
        all_columns = scenario_df.columns.tolist()
        data_columns = [col for col in all_columns if col not in ['block', 'key']]
        columns_to_drop = [col for col in data_columns if col != scenario_column]
        scenario_df = scenario_df.drop(columns=columns_to_drop)

        print(f"  - Using scenario column: '{scenario_column}'")

        # Print current CO2 constraint if present
        co2_mask = (scenario_df['block'] == 'scenario') & (scenario_df['key'] == 'co2_max')
        if co2_mask.any():
            co2_value = scenario_df.loc[co2_mask, scenario_column].values[0]
            if pd.notna(co2_value) and co2_value != '' and co2_value != 'None':
                print(f"  - CO2 limit: {co2_value} kg")

        # Update project duration for this stage
        prj_mask = (scenario_df['block'] == 'scenario') & (scenario_df['key'] == 'prj_duration')
        if prj_mask.any():
            scenario_df.loc[prj_mask, scenario_column] = self.config.stage_duration_years
            print(f"  - Stage duration: {self.config.stage_duration_years} years")

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

        # 5. Set invest_max to prevent unbounded optimization
        # This is critical for multi-stage: revoletion doesn't know about future stages,
        # so we need reasonable bounds to prevent unrealistic investment in any single stage
        scenario_df = self._update_invest_max(scenario_df, stage_year, scenario_column)

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

        Generic implementation - loops over investable blocks from config.

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
        print("  - Inheriting capacities from previous stage:")

        for block_cfg in self.config.investable_blocks:
            # Key in results dict (e.g., 'pv_size_total', 'ess_size_total')
            result_key = f"{block_cfg.name}_size_total"

            if result_key in prev_results and prev_results[result_key] is not None:
                size = prev_results[result_key]

                # Update size_existing in scenario CSV
                mask = (df['block'] == block_cfg.name) & (df['key'] == 'size_existing')
                if mask.any():
                    df.loc[mask, column] = size

                    # Generic pretty printing using unit helper
                    unit = get_unit(block_cfg.name)
                    if unit in ['kW', 'kWh']:
                        print(f"    • {block_cfg.name}: {size/1000:.1f} {unit} inherited")
                    elif unit == 'vehicles':
                        print(f"    • {block_cfg.name}: {int(size):,} {unit} inherited")
                    else:
                        print(f"    • {block_cfg.name}: {size:.0f} {unit} inherited")

        # Special handling for grid g2s/s2g (bidirectional connections)
        if 'grid_size_g2s' in prev_results and prev_results['grid_size_g2s'] is not None:
            grid_g2s = prev_results['grid_size_g2s']
            mask = (df['block'] == 'grid') & (df['key'] == 'size_g2s_existing')
            if mask.any():
                df.loc[mask, column] = grid_g2s
                print(f"    • grid (g2s): {grid_g2s/1000:.1f} kW inherited")

        if 'grid_size_s2g' in prev_results and prev_results['grid_size_s2g'] is not None:
            grid_s2g = prev_results['grid_size_s2g']
            mask = (df['block'] == 'grid') & (df['key'] == 'size_s2g_existing')
            if mask.any():
                df.loc[mask, column] = grid_s2g
                print(f"    • grid (s2g): {grid_s2g/1000:.1f} kW inherited")

        return df

    def _update_costs(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update technology costs based on stage year.

        Generic implementation - loops over technology costs from config.

        Parameters:
        -----------
        df : DataFrame
            Scenario DataFrame
        stage_year : int
            Year of this stage
        column : str
            Column to update

        Returns:
        --------
        DataFrame : Updated scenario
        """
        base_year = self.config.tech_costs[list(self.config.tech_costs.keys())[0]].base_year
        years_elapsed = stage_year - base_year

        # Always apply config base costs, even in base year (years_elapsed == 0)
        # This ensures sensitivity configs with different base_cost are applied
        for tech_name, cost_config in self.config.tech_costs.items():
            # Calculate cost for this stage year
            new_cost = cost_config.get_cost(stage_year)

            # Find matching blocks (pattern match: 'pv' matches 'pv', 'pv1', etc.)
            matching_blocks = [b for b in self.config.investable_blocks
                             if tech_name in b.name]

            for block_cfg in matching_blocks:
                mask = (df['block'] == block_cfg.name) & (df['key'] == block_cfg.cost_param)
                if mask.any():
                    old_cost = df.loc[mask, column].values[0]
                    if pd.notna(old_cost) and old_cost != '' and old_cost != 'None':
                        old_cost = float(old_cost)
                        df.loc[mask, column] = new_cost

                        # Only print if cost actually changed
                        if abs(old_cost - new_cost) > 0.001:
                            decline_pct = -cost_config.annual_decline_rate * 100
                            if 'pv' in tech_name:
                                print(f"  - {tech_name.upper()} cost: ${old_cost:.2f}/W → "
                                     f"${new_cost:.2f}/W ({decline_pct:.0f}%/yr)")
                            elif 'ess' in tech_name:
                                print(f"  - {tech_name.upper()} cost: ${old_cost:.3f}/Wh → "
                                     f"${new_cost:.3f}/Wh ({decline_pct:.0f}%/yr)")
                            else:
                                print(f"  - {tech_name} cost: {old_cost:.3f} → {new_cost:.3f}")

        return df

    def _update_demand(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update demand/fleet size based on growth projections.

        Generic implementation - uses config for growth rate and base values.
        Also handles bev_log scaling when fleet grows.

        Parameters:
        -----------
        df : DataFrame
            Scenario DataFrame
        stage_year : int
            Year of this stage
        column : str
            Column to update

        Returns:
        --------
        DataFrame : Updated scenario
        """
        years_elapsed = stage_year - self.config.demand_base_year

        if years_elapsed > 0 and self.config.demand_annual_growth_rate > 0:
            growth_factor = (1 + self.config.demand_annual_growth_rate) ** years_elapsed

            # Update each demand block based on config
            for block_cfg in self.config.demand_blocks:
                # Update fleet size if this block has size_param (bev,num)
                if hasattr(block_cfg, 'size_param') and block_cfg.size_param:
                    mask = (df['block'] == block_cfg.name) & (df['key'] == block_cfg.size_param)
                    if mask.any():
                        base_val = df.loc[mask, column].values[0]
                        if pd.notna(base_val) and base_val != '' and base_val != 'None':
                            base_val = int(float(base_val))
                            new_val = int(base_val * growth_factor)
                            df.loc[mask, column] = new_val

                            if 'bev' in block_cfg.name:
                                print(f"  - Fleet size: {base_val} vehicles → "
                                     f"{new_val} vehicles "
                                     f"(+{self.config.demand_annual_growth_rate*100:.0f}%/yr)")

                                # Scale bev_log if enabled
                                if self.config.demand_scale_bev_log and new_val > base_val:
                                    df = self._scale_bev_log_for_stage(
                                        df, column, stage_year, base_val, new_val
                                    )

                # Update consumption if this block has consumption_param
                if hasattr(block_cfg, 'consumption_param') and block_cfg.consumption_param:
                    mask = (df['block'] == block_cfg.name) & (df['key'] == block_cfg.consumption_param)
                    if mask.any():
                        base_val = df.loc[mask, column].values[0]
                        if pd.notna(base_val) and base_val != '' and base_val != 'None':
                            base_val = float(base_val)
                            new_val = base_val * growth_factor
                            df.loc[mask, column] = new_val
                            print(f"  - Annual consumption: {base_val/1e6:.2f} MWh → "
                                 f"{new_val/1e6:.2f} MWh")

        return df

    def _scale_bev_log_for_stage(
        self,
        df: pd.DataFrame,
        column: str,
        stage_year: int,
        base_vehicles: int,
        target_vehicles: int
    ) -> pd.DataFrame:
        """
        Create scaled bev_log file for this stage and update scenario.

        Parameters:
        -----------
        df : DataFrame
            Scenario DataFrame
        column : str
            Column to update
        stage_year : int
            Year of this stage
        base_vehicles : int
            Original number of vehicles
        target_vehicles : int
            Target number of vehicles after growth

        Returns:
        --------
        DataFrame : Updated scenario with new bev_log filename
        """
        # Get current bev_log filename from scenario
        filename_mask = (df['block'] == 'bev') & (df['key'] == 'filename')
        if not filename_mask.any():
            print(f"  ⚠️  No bev,filename found - skipping bev_log scaling")
            return df

        base_filename = df.loc[filename_mask, column].values[0]

        # Determine paths
        # The bev_log filename in scenario might be relative (e.g., "timeseries/bev_log_test")
        # We need to resolve it relative to the input directory (parent of scenarios/)
        # Template is in inputs/schmid/scenarios/, input dir is inputs/schmid/
        input_dir = self.template_path.parent.parent  # Go up from scenarios/ to schmid/
        base_log_path = input_dir / f"{base_filename}.csv"

        if not base_log_path.exists():
            print(f"  ⚠️  Base bev_log not found: {base_log_path} - skipping scaling")
            return df

        # Create output filename and path
        new_filename = f"bev_log_stage_{stage_year}"
        output_path = self.config.stage_scenarios_dir / f"{new_filename}.csv"

        # Scale the bev_log
        print(f"  - Scaling bev_log for fleet growth:")
        scale_bev_log(
            base_log_path=base_log_path,
            output_path=output_path,
            base_vehicles=base_vehicles,
            target_vehicles=target_vehicles,
            seed=stage_year  # Use stage year as seed for reproducibility
        )

        # Update scenario to point to new bev_log
        # Compute relative path from input_dir to stage_scenarios_dir
        # input_dir is inputs/schmid/, stage_scenarios_dir is runs/<name>/stages/
        try:
            relative_path = os.path.relpath(
                self.config.stage_scenarios_dir / new_filename,
                input_dir
            )
        except ValueError:
            # Fallback if on different drives (Windows)
            relative_path = str(self.config.stage_scenarios_dir / new_filename)
        
        df.loc[filename_mask, column] = relative_path

        return df

    def _update_co2_limits(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Update CO2 limits based on decarbonization pathway.

        Uses config.calculate_co2_limit() method (supports multiple pathway types).

        Parameters:
        -----------
        df : DataFrame
            Scenario DataFrame
        stage_year : int
            Year of this stage
        column : str
            Column to update

        Returns:
        --------
        DataFrame : Updated scenario
        """
        # Calculate limit from config
        co2_limit_new = self.config.calculate_co2_limit(stage_year)

        # Skip if limit is very high (effectively disabled)
        if co2_limit_new >= 999999999:
            return df

        # Update CO2 limit in scenario
        co2_mask = (df['block'] == 'scenario') & (df['key'] == 'co2_max')
        if co2_mask.any():
            co2_limit_old = df.loc[co2_mask, column].values[0]
            df.loc[co2_mask, column] = co2_limit_new

            if pd.notna(co2_limit_old) and co2_limit_old != '' and co2_limit_old != 'None':
                co2_limit_old = float(co2_limit_old)
                print(f"  - CO2 limit: {co2_limit_old:.0f} kg → {co2_limit_new:.0f} kg "
                     f"(decarbonization pathway)")
            else:
                print(f"  - CO2 limit: None → {co2_limit_new:.0f} kg "
                     f"(decarbonization pathway enabled)")

        return df

    def _update_invest_max(
        self,
        df: pd.DataFrame,
        stage_year: int,
        column: str
    ) -> pd.DataFrame:
        """
        Set invest_max to prevent unbounded optimization problems.

        In multi-stage optimization, each revoletion run doesn't know about future stages.
        Without invest_max, the optimizer may invest infinitely when compensate_sim_prj=True
        makes investment costs appear relatively cheap compared to operational costs.

        The invest_max is calculated based on expected stage energy demand to ensure
        realistic investment levels while still allowing necessary capacity expansion.

        Parameters:
        -----------
        df : DataFrame
            Scenario DataFrame
        stage_year : int
            Year of this stage
        column : str
            Column to update

        Returns:
        --------
        DataFrame : Updated scenario
        """
        # Calculate expected fleet size for this stage
        fleet_size = self.config.calculate_fleet_size(stage_year)

        # Estimate annual energy demand (kWh)
        # Conservative estimate: 15,000 kWh/vehicle/year for BEV fleet
        energy_per_vehicle_kwh = 15000
        annual_energy_demand_kwh = fleet_size * energy_per_vehicle_kwh

        # Calculate reasonable investment cap using config parameters
        # This covers PV + ESS + grid upgrades while preventing runaway investment
        investment_budget_per_kwh = self.config.invest_budget_per_kwh

        # Scale by stage duration (longer stages need more investment headroom)
        stage_years = self.config.stage_duration_years
        invest_max = annual_energy_demand_kwh * investment_budget_per_kwh * stage_years

        # Update invest_max in scenario (only if not explicitly set)
        invest_mask = (df['block'] == 'scenario') & (df['key'] == 'invest_max')
        if invest_mask.any():
            old_val = df.loc[invest_mask, column].values[0]
            # Only override if the value is NaN/None (not explicitly set)
            if pd.isna(old_val):
                df.loc[invest_mask, column] = invest_max
                print(f"  - invest_max: {old_val} → ${invest_max:,.0f} "
                      f"(based on {fleet_size} vehicles × {stage_years} years)")
            else:
                print(f"  - invest_max: ${float(old_val):,.0f} (explicitly set, not overriding)")
        else:
            # If invest_max row doesn't exist, we should add it
            # But for now, just warn - the template should include it
            print(f"  ⚠ invest_max not found in template - optimizer may be unbounded!")

        return df

    def extract_scenario_column_names(self) -> list:
        """
        Get list of scenario column names from template.

        Returns:
        --------
        list : Column names (excluding 'block' and 'key')
        """
        return [col for col in self.template.columns if col not in ['block', 'key']]
