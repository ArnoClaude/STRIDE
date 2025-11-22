"""
STRIDE Multi-Stage Sequential Optimizer

Sequential temporal resource investment for depot electrification.
"""

from .sequential_optimizer import SequentialStageOptimizer
from .scenario_builder import ScenarioBuilder
from .results_parser import ResultsParser

__all__ = [
    'SequentialStageOptimizer',
    'ScenarioBuilder',
    'ResultsParser',
]

__version__ = '0.1.0'
__author__ = 'Arno Claude'
