"""
STRIDE Multi-Stage Sequential Optimizer

Sequential temporal resource investment for depot electrification.
"""

from .config_loader import MultiStageConfig
from .sequential_optimizer import SequentialStageOptimizer
from .scenario_builder import ScenarioBuilder
from .results_parser import ResultsParser

__all__ = [
    'MultiStageConfig',
    'SequentialStageOptimizer',
    'ScenarioBuilder',
    'ResultsParser',
]

__version__ = '0.1.0'
__author__ = 'Arno Claude'
