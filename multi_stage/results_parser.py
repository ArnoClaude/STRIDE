"""
Results Parser for REVOL-E-TION multi-stage optimization.

Extracts metrics from REVOL-E-TION summary CSVs and prepares data
for feeding into next stage.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from .config_loader import MultiStageConfig


@dataclass
class InvestmentResult:
    """Investment result for a single block."""
    block_name: str
    size_existing: float  # W or Wh
    size_invested: float  # W or Wh (new in this stage)
    total_size: float  # W or Wh (existing + invested)
    capex: Optional[float] = None
    opex: Optional[float] = None


@dataclass
class StageMetrics:
    """Economic and operational metrics for a stage."""
    stage_year: int
    status: str
    result_dir: str

    # Economics
    npv: Optional[float]
    capex_prj: Optional[float]
    opex_prj: Optional[float]
    lcoe_total: Optional[float]

    # Investments
    investments: List[InvestmentResult]

    # Energy flows (simulation period)
    grid_import_sim_kwh: Optional[float]
    grid_export_sim_kwh: Optional[float]
    pv_generation_sim_kwh: Optional[float]

    # CO2 emissions
    co2_sim_kg: Optional[float]
    co2_prj_kg: Optional[float]
    co2_extrapolation_factor: float

    # Discounting
    discount_factor: float
    npv_discounted: Optional[float]

    # Durations
    sim_duration_days: Optional[float]
    prj_duration_years: Optional[float]


class ResultsParser:
    """
    Parse REVOL-E-TION output files to extract investment decisions
    and economic metrics.

    Config-driven implementation - extracts investable blocks based on config.
    """

    def __init__(self, config: MultiStageConfig):
        """
        Parameters:
        -----------
        config : MultiStageConfig
            Configuration object defining blocks to extract
        """
        self.config = config

    def parse_stage_results(
        self,
        result_dir: Path,
        stage_year: int
    ) -> Dict:
        """
        Parse REVOL-E-TION results for a single stage.

        Parameters:
        -----------
        result_dir : Path
            Directory containing REVOL-E-TION results
        stage_year : int
            Year of this stage (e.g., 2025, 2030)

        Returns:
        --------
        dict : Stage results including capacities and economics
              (compatible with legacy code - returns dict not StageMetrics)
        """
        # Check scenario status FIRST
        status_file = result_dir / f"{result_dir.name}_scenarios_status.csv"
        scenario_status = 'unknown'
        if status_file.exists():
            try:
                status_df = pd.read_csv(status_file)
                if not status_df.empty:
                    scenario_status = status_df.iloc[-1]['status']
            except Exception as e:
                print(f"  ⚠️  Warning: Could not read status file: {e}")

        # Handle infeasible scenarios (no summary CSV generated)
        summary_files = list(result_dir.glob("*_summary.csv"))
        if not summary_files:
            if scenario_status == 'infeasible':
                print(f"  ⚠️  Scenario was INFEASIBLE - no summary generated")
                return self._create_infeasible_results(stage_year, result_dir)
            else:
                raise FileNotFoundError(f"No summary CSV found in {result_dir}")

        summary_file = summary_files[0]
        try:
            df = pd.read_csv(summary_file)
        except Exception as e:
            print(f"  ⚠️  Warning: Could not read summary file: {e}")
            return self._create_infeasible_results(stage_year, result_dir)

        # Helper function to extract values
        def get_value(block: str, key: str) -> Optional[float]:
            mask = (df['Block'] == block) & (df['Key'] == key)
            if mask.any():
                # Get last column (the scenario we ran)
                val = df.loc[mask, df.columns[-1]].values[0]
                if val == '' or pd.isna(val):
                    return None
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
            return None

        # Extract results - GENERIC based on config
        results = {
            # Metadata
            'stage_year': stage_year,
            'status': scenario_status,
            'result_dir': str(result_dir),

            # Economics (project-level, already in 5-year stage context)
            'npv': get_value('scenario', 'npv'),
            'npc': get_value('scenario', 'npc'),
            'capex_prj': get_value('scenario', 'capex_prj'),
            'opex_prj': get_value('scenario', 'opex_prj'),
            'lcoe_total': get_value('scenario', 'lcoe_total'),
        }

        # Extract investable block capacities (GENERIC)
        for block_cfg in self.config.investable_blocks:
            # Total capacity (existing + new)
            total_key = f"{block_cfg.name}_size_total"
            results[total_key] = get_value(block_cfg.name, 'size_total')

            # New investments (this stage only)
            invest_key = f"{block_cfg.name}_size_invest"
            results[invest_key] = get_value(block_cfg.name, 'size_additional')

        # Special handling for grid (bidirectional: g2s and s2g)
        # This is SPECIFIC because grid block has multiple size parameters
        results['grid_size_g2s'] = get_value('grid', 'size_g2s_total')
        results['grid_size_s2g'] = get_value('grid', 'size_s2g_total')
        results['grid_size_g2s_invest'] = get_value('grid', 'size_g2s_additional')

        # Energy metrics (simulation period)
        results['grid_import_sim_kwh'] = (get_value('grid', 'e_del_sim') / 1000
                                         if get_value('grid', 'e_del_sim') else 0)
        results['grid_export_sim_kwh'] = (get_value('grid', 'e_pro_sim') / 1000
                                         if get_value('grid', 'e_pro_sim') else 0)
        results['pv_generation_sim_kwh'] = (get_value('pv', 'e_pro_sim') / 1000
                                           if get_value('pv', 'e_pro_sim') else 0)

        # CO2 emissions (simulation period)
        # Note: Using grid CO2 factor if available, defaulting to 0.4 kg/kWh
        results['co2_sim_kg'] = ((get_value('grid', 'e_del_sim') / 1000 *
                                 (get_value('grid', 'co2_spec_g2s') or 0.4))
                                if get_value('grid', 'e_del_sim') else 0)

        # Calculate project-level CO2 emissions (extrapolated from simulation)
        # NOTE: REVOL-E-TION uses 'prj_duration_yrs' in output, not 'prj_duration'
        sim_duration_days = get_value('scenario', 'sim_duration') or 50
        prj_duration_years = get_value('scenario', 'prj_duration_yrs') or 25

        # Get compensate flag (boolean field)
        compensate_mask = (df['Block'] == 'scenario') & (df['Key'] == 'compensate_sim_prj')
        compensate = True  # Default to True
        if compensate_mask.any():
            compensate_val = df.loc[compensate_mask, df.columns[-1]].values[0]
            if compensate_val in ['True', 'true', True, 1, '1']:
                compensate = True
            elif compensate_val in ['False', 'false', False, 0, '0']:
                compensate = False

        # Extrapolation factor: project days / simulation days
        co2_extrapolation_factor = ((prj_duration_years * 365) / sim_duration_days
                                   if compensate else 1.0)

        results['sim_duration_days'] = sim_duration_days
        results['prj_duration_years'] = prj_duration_years
        results['co2_extrapolation_factor'] = co2_extrapolation_factor
        results['co2_prj_kg'] = results['co2_sim_kg'] * co2_extrapolation_factor

        # Discount NPV to present value (base year = first stage)
        base_year = min(self.config.stages)
        years_from_base = stage_year - base_year
        discount_factor = 1 / ((1 + self.config.wacc) ** years_from_base)
        results['discount_factor'] = discount_factor
        results['npv_discounted'] = (results['npv'] * discount_factor
                                    if results['npv'] else None)

        return results

    def _create_infeasible_results(self, stage_year: int, result_dir: Path) -> Dict:
        """Create results dict for infeasible scenario (all None values)."""
        base_year = min(self.config.stages)
        years_from_base = stage_year - base_year
        discount_factor = 1 / ((1 + self.config.wacc) ** years_from_base)

        results = {
            'stage_year': stage_year,
            'status': 'infeasible',
            'result_dir': str(result_dir),
            'npv': None,
            'npc': None,
            'capex_prj': None,
            'opex_prj': None,
            'lcoe_total': None,
            'grid_import_sim_kwh': None,
            'grid_export_sim_kwh': None,
            'pv_generation_sim_kwh': None,
            'co2_sim_kg': None,
            'sim_duration_days': None,
            'prj_duration_years': None,
            'co2_extrapolation_factor': None,
            'co2_prj_kg': None,
            'discount_factor': discount_factor,
            'npv_discounted': None,
        }

        # Add None values for all investable blocks (GENERIC)
        for block_cfg in self.config.investable_blocks:
            results[f"{block_cfg.name}_size_total"] = None
            results[f"{block_cfg.name}_size_invest"] = None

        # Special handling for grid
        results['grid_size_g2s'] = None
        results['grid_size_s2g'] = None
        results['grid_size_g2s_invest'] = None

        return results

    def get_latest_result_dir(self, results_base_dir: Path) -> Path:
        """
        Find the most recently created REVOL-E-TION results directory.

        Parameters:
        -----------
        results_base_dir : Path
            Base directory containing result subdirectories

        Returns:
        --------
        Path : Most recent results directory
        """
        result_dirs = sorted(
            [p for p in results_base_dir.glob("*") if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not result_dirs:
            raise FileNotFoundError(f"No result directories found in {results_base_dir}")

        return result_dirs[0]

    def aggregate_multi_stage_results(
        self,
        stage_results: Dict[int, Dict]
    ) -> Dict:
        """
        Aggregate results across all stages.

        Parameters:
        -----------
        stage_results : dict
            Dictionary mapping year → stage results

        Returns:
        --------
        dict : Aggregated multi-stage results
        """
        # Calculate total NPV (sum of discounted stage NPVs)
        total_npv = sum(
            r['npv_discounted']
            for r in stage_results.values()
            if r.get('npv_discounted') is not None
        )

        # Total CAPEX (sum across all stages)
        total_capex = sum(
            r['capex_prj']
            for r in stage_results.values()
            if r.get('capex_prj') is not None
        )

        # Build investment timeline DataFrame
        timeline_data = []
        for year, results in sorted(stage_results.items()):
            # Helper to safely convert W/Wh to kW/kWh (handle None)
            def to_kw(value):
                return (value / 1000) if value is not None else 0

            timeline_data.append({
                'year': year,
                'pv_total_kw': to_kw(results.get('pv_size_total')),
                'pv_new_kw': to_kw(results.get('pv_size_invest')),
                'ess_total_kwh': to_kw(results.get('ess_size_total')),
                'ess_new_kwh': to_kw(results.get('ess_size_invest')),
                'capex': results.get('capex_prj') or 0,
                'npv': results.get('npv') or 0,
                'npv_discounted': results.get('npv_discounted') or 0,
            })

        investment_timeline = pd.DataFrame(timeline_data)

        return {
            'total_npv': total_npv,
            'total_capex': total_capex,
            'investment_timeline': investment_timeline,
            'stage_results': stage_results,
        }
