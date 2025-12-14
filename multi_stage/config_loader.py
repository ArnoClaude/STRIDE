"""
Configuration loader for multi-stage optimization.

Loads YAML configuration files with validation and type safety.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class TechCostConfig:
    """Technology cost evolution configuration."""
    base_year: int
    base_cost: float  # $/W or $/Wh
    annual_decline_rate: float

    def get_cost(self, year: int) -> float:
        """Calculate cost for a given year using exponential decline."""
        years_elapsed = year - self.base_year
        if years_elapsed < 0:
            raise ValueError(f"Year {year} is before base year {self.base_year}")
        return self.base_cost * ((1 - self.annual_decline_rate) ** years_elapsed)


@dataclass
class BlockConfig:
    """Configuration for a single block (investable or demand)."""
    name: str
    cost_param: Optional[str] = None
    size_param: Optional[str] = None
    consumption_param: Optional[str] = None


@dataclass
class MultiStageConfig:
    """Complete multi-stage optimization configuration."""

    # Stage configuration
    stages: List[int]
    stage_duration_years: int

    # Technology costs
    tech_costs: Dict[str, TechCostConfig]

    # Demand configuration
    demand_base_year: int
    demand_base_num_vehicles: int
    demand_annual_growth_rate: float

    # Emissions configuration
    emissions_pathway_type: str
    emissions_base_year: int
    emissions_base_limit_kg: float
    emissions_final_year: int
    emissions_final_limit_kg: float

    # Economics
    wacc: float

    # Block definitions
    investable_blocks: List[BlockConfig]
    demand_blocks: List[BlockConfig]

    # REVOLETION paths
    revoletion_settings_path: Path
    revoletion_results_base_dir: Path

    # Output paths
    stage_scenarios_dir: Path
    summary_output_dir: Path

    # Investment constraints (prevents unbounded optimization)
    # invest_budget_per_kwh: $ allowed per kWh of annual fleet energy demand
    invest_budget_per_kwh: float = 3.0

    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None,
                  default_config_path: Optional[str] = None) -> 'MultiStageConfig':
        """
        Load configuration from YAML file(s).

        Parameters
        ----------
        config_path : str, optional
            Path to user configuration file (overrides defaults)
        default_config_path : str, optional
            Path to default configuration file

        Returns
        -------
        MultiStageConfig
            Loaded and validated configuration
        """
        # Load default config
        if default_config_path is None:
            default_config_path = Path(__file__).parent / "config" / "default.yaml"

        with open(default_config_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Merge with user config if provided
        if config_path is not None:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
            config_dict = deep_merge(config_dict, user_config)

        # Parse into dataclass
        return cls._from_dict(config_dict)

    @classmethod
    def _from_dict(cls, cfg: Dict[str, Any]) -> 'MultiStageConfig':
        """Parse dictionary into MultiStageConfig dataclass."""

        # Determine repo root (relative paths are resolved relative to this)
        # Config loader is in multi_stage/, so repo root is parent directory
        repo_root = Path(__file__).parent.parent

        # Parse technology costs
        tech_costs = {}
        for tech_name, tech_cfg in cfg['technology_costs'].items():
            if tech_name == 'pv':
                base_cost = tech_cfg['base_cost_per_w']
            elif tech_name == 'ess':
                base_cost = tech_cfg['base_cost_per_wh']
            else:
                base_cost = tech_cfg.get('base_cost', 0)

            tech_costs[tech_name] = TechCostConfig(
                base_year=tech_cfg['base_year'],
                base_cost=base_cost,
                annual_decline_rate=tech_cfg['annual_decline_rate']
            )

        # Parse investable blocks
        investable_blocks = [
            BlockConfig(**block_cfg)
            for block_cfg in cfg['blocks']['investable']
        ]

        # Parse demand blocks
        demand_blocks = [
            BlockConfig(**block_cfg)
            for block_cfg in cfg['blocks']['demand']
        ]

        # Helper to resolve paths (relative paths are resolved relative to repo root)
        def resolve_path(path_str: str) -> Path:
            p = Path(path_str)
            if p.is_absolute():
                return p
            else:
                return (repo_root / p).resolve()

        # Get optional investment constraint parameters (with defaults)
        economics_cfg = cfg.get('economics', {})
        invest_budget_per_kwh = economics_cfg.get('invest_budget_per_kwh', 3.0)

        # Create config object
        config = cls(
            stages=cfg['stages']['years'],
            stage_duration_years=cfg['stages']['duration_years'],
            tech_costs=tech_costs,
            demand_base_year=cfg['demand']['base_year'],
            demand_base_num_vehicles=cfg['demand']['base_num_vehicles'],
            demand_annual_growth_rate=cfg['demand']['annual_growth_rate'],
            emissions_pathway_type=cfg['emissions']['pathway_type'],
            emissions_base_year=cfg['emissions']['base_year'],
            emissions_base_limit_kg=cfg['emissions']['base_limit_kg'],
            emissions_final_year=cfg['emissions']['final_year'],
            emissions_final_limit_kg=cfg['emissions']['final_limit_kg'],
            wacc=cfg['economics']['wacc'],
            invest_budget_per_kwh=invest_budget_per_kwh,
            investable_blocks=investable_blocks,
            demand_blocks=demand_blocks,
            revoletion_settings_path=resolve_path(cfg['revoletion']['settings_path']),
            revoletion_results_base_dir=resolve_path(cfg['revoletion']['results_base_dir']),
            stage_scenarios_dir=resolve_path(cfg['output']['stage_scenarios_dir']),
            summary_output_dir=resolve_path(cfg['output']['summary_output_dir'])
        )

        # Validate
        config.validate()

        return config

    def validate(self):
        """Validate configuration consistency."""

        # Check stages are sorted and >= base_year
        if not all(self.stages[i] < self.stages[i+1] for i in range(len(self.stages)-1)):
            raise ValueError("Stages must be in ascending order")

        # Check final year >= max(stages) (can be equal to last stage)
        if self.emissions_final_year < max(self.stages):
            raise ValueError(f"Emissions final year ({self.emissions_final_year}) "
                           f"must be >= last stage ({max(self.stages)})")

        # Check decline rates in valid range
        for tech_name, tech_config in self.tech_costs.items():
            if not (0 <= tech_config.annual_decline_rate < 1):
                raise ValueError(f"{tech_name} decline rate must be in [0, 1), "
                               f"got {tech_config.annual_decline_rate}")

        # Check demand growth rate is positive
        if self.demand_annual_growth_rate <= 0:
            raise ValueError(f"Demand growth rate must be positive, "
                           f"got {self.demand_annual_growth_rate}")

        # Check WACC is positive
        if self.wacc <= 0:
            raise ValueError(f"WACC must be positive, got {self.wacc}")

        # Check block names are unique
        all_block_names = ([b.name for b in self.investable_blocks] +
                          [b.name for b in self.demand_blocks])
        if len(all_block_names) != len(set(all_block_names)):
            raise ValueError("Block names must be unique")

    def calculate_co2_limit(self, year: int) -> float:
        """
        Calculate CO2 limit for a given year based on pathway.

        Parameters
        ----------
        year : int
            Year to calculate limit for

        Returns
        -------
        float
            CO2 limit in kg
        """
        if self.emissions_pathway_type == 'linear':
            # Linear interpolation
            if year <= self.emissions_base_year:
                return self.emissions_base_limit_kg
            elif year >= self.emissions_final_year:
                return self.emissions_final_limit_kg
            else:
                # Interpolate
                fraction = ((year - self.emissions_base_year) /
                           (self.emissions_final_year - self.emissions_base_year))
                return (self.emissions_base_limit_kg +
                       fraction * (self.emissions_final_limit_kg -
                                  self.emissions_base_limit_kg))
        else:
            raise NotImplementedError(f"Pathway type '{self.emissions_pathway_type}' "
                                    "not yet implemented")

    def calculate_fleet_size(self, year: int) -> int:
        """Calculate fleet size for a given year using exponential growth."""
        years_elapsed = year - self.demand_base_year
        if years_elapsed < 0:
            raise ValueError(f"Year {year} is before base year {self.demand_base_year}")
        return int(self.demand_base_num_vehicles *
                  ((1 + self.demand_annual_growth_rate) ** years_elapsed))

    def get_discount_factor(self, year: int) -> float:
        """Calculate NPV discount factor for a given year."""
        years_from_base = year - min(self.stages)
        return 1 / ((1 + self.wacc) ** years_from_base)


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries (override values into base).

    Parameters
    ----------
    base : dict
        Base dictionary
    override : dict
        Override dictionary (takes precedence)

    Returns
    -------
    dict
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result
