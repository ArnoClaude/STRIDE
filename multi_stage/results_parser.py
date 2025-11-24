"""
Results Parser for REVOL-E-TION multi-stage optimization.

Extracts metrics from REVOL-E-TION summary CSVs and prepares data
for feeding into next stage.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd


class ResultsParser:
    """
    Parse REVOL-E-TION output files to extract investment decisions
    and economic metrics.
    """

    def __init__(self):
        pass

    def parse_stage_results(
        self,
        result_dir: Path,
        stage_year: int,
        discount_rate: float = 0.09
    ) -> Dict:
        """
        Parse REVOL-E-TION results for a single stage.

        Parameters:
        -----------
        result_dir : Path
            Directory containing REVOL-E-TION results
        stage_year : int
            Year of this stage (e.g., 2025, 2030)
        discount_rate : float
            WACC for NPV discounting

        Returns:
        --------
        dict : Stage results including capacities and economics
        """
        # Check scenario status FIRST
        status_file = result_dir / f"{result_dir.name}_scenarios_status.csv"
        scenario_status = 'unknown'
        if status_file.exists():
            status_df = pd.read_csv(status_file)
            if not status_df.empty:
                scenario_status = status_df.iloc[-1]['status']

        # Handle infeasible scenarios (no summary CSV generated)
        summary_files = list(result_dir.glob("*_summary.csv"))
        if not summary_files:
            if scenario_status == 'infeasible':
                print(f"  ⚠️  Scenario was INFEASIBLE - no summary generated")
                return {
                    'stage_year': stage_year,
                    'status': 'infeasible',
                    'result_dir': str(result_dir),
                    'npv': None,
                    'npc': None,
                    'capex_prj': None,
                    'opex_prj': None,
                    'lcoe_total': None,
                    'pv_size_total': None,
                    'ess_size_total': None,
                    'grid_size_g2s': None,
                    'grid_size_s2g': None,
                    'pv_size_invest': None,
                    'ess_size_invest': None,
                    'grid_size_g2s_invest': None,
                    'grid_import_sim_kwh': None,
                    'grid_export_sim_kwh': None,
                    'pv_generation_sim_kwh': None,
                    'co2_sim_kg': None,
                    'sim_duration_days': None,
                    'prj_duration_years': None,
                    'co2_extrapolation_factor': None,
                    'co2_prj_kg': None,
                    'discount_factor': 1 / ((1 + discount_rate) ** (stage_year - 2025)),
                    'npv_discounted': None,
                }
            else:
                raise FileNotFoundError(f"No summary CSV found in {result_dir}")

        summary_file = summary_files[0]
        df = pd.read_csv(summary_file)

        # Helper function to extract values
        def get_value(block: str, key: str) -> Optional[float]:
            mask = (df['Block'] == block) & (df['Key'] == key)
            if mask.any():
                # Get last column (the scenario we ran)
                val = df.loc[mask, df.columns[-1]].values[0]
                if val == '' or pd.isna(val):
                    return None
                return float(val)
            return None

        # Extract results
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

            # Capacities - TOTAL (existing + new investments)
            # These will become size_existing for next stage
            'pv_size_total': get_value('pv', 'size_total'),  # W
            'ess_size_total': get_value('ess', 'size_total'),  # Wh
            'grid_size_g2s': get_value('grid', 'size_g2s_total'),  # W
            'grid_size_s2g': get_value('grid', 'size_s2g_total'),  # W

            # NEW investments (this stage only)
            'pv_size_invest': get_value('pv', 'size_additional'),  # W
            'ess_size_invest': get_value('ess', 'size_additional'),  # Wh
            'grid_size_g2s_invest': get_value('grid', 'size_g2s_additional'),  # W

            # Energy metrics (simulation period)
            'grid_import_sim_kwh': get_value('grid', 'e_del_sim') / 1000 if get_value('grid', 'e_del_sim') else 0,
            'grid_export_sim_kwh': get_value('grid', 'e_pro_sim') / 1000 if get_value('grid', 'e_pro_sim') else 0,
            'pv_generation_sim_kwh': get_value('pv', 'e_pro_sim') / 1000 if get_value('pv', 'e_pro_sim') else 0,

            # CO2 emissions (simulation period)
            # Note: Using grid CO2 factor if available, defaulting to 0.4 kg/kWh
            'co2_sim_kg': (get_value('grid', 'e_del_sim') / 1000 *
                          (get_value('grid', 'co2_spec_g2s') or 0.4)) if get_value('grid', 'e_del_sim') else 0,
        }

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
        co2_extrapolation_factor = (prj_duration_years * 365) / sim_duration_days if compensate else 1.0

        results['sim_duration_days'] = sim_duration_days
        results['prj_duration_years'] = prj_duration_years
        results['co2_extrapolation_factor'] = co2_extrapolation_factor
        results['co2_prj_kg'] = results['co2_sim_kg'] * co2_extrapolation_factor

        # Discount NPV to present value (2025)
        years_from_2025 = stage_year - 2025
        discount_factor = 1 / ((1 + discount_rate) ** years_from_2025)
        results['discount_factor'] = discount_factor
        results['npv_discounted'] = results['npv'] * discount_factor if results['npv'] else None

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
