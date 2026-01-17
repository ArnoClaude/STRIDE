"""
Run manifest generation for STRIDE.

Creates a manifest.yaml file capturing all inputs, parameters, and environment
for full traceability and reproducibility of runs.
"""

import hashlib
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    if not file_path.exists():
        return "file_not_found"
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:16]  # Truncate for readability


def get_git_info(repo_path: Path) -> Dict[str, Any]:
    """Get git repository information."""
    try:
        # Get current commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        commit = result.stdout.strip() if result.returncode == 0 else None
        
        # Get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = result.stdout.strip() if result.returncode == 0 else None
        
        # Check if working directory is dirty
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        dirty = bool(result.stdout.strip()) if result.returncode == 0 else None
        
        # Get short diff if dirty (just file names, not full diff)
        changed_files = None
        if dirty:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                changed_files = result.stdout.strip().split('\n')
        
        return {
            "commit": commit[:12] if commit else None,
            "commit_full": commit,
            "branch": branch,
            "dirty": dirty,
            "changed_files": changed_files
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {
            "commit": None,
            "branch": None,
            "dirty": None,
            "changed_files": None
        }


def get_submodule_info(repo_path: Path, submodule_name: str) -> Dict[str, Any]:
    """Get git submodule commit information."""
    try:
        # Get submodule commit hash
        result = subprocess.run(
            ["git", "submodule", "status", submodule_name],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            # Format: " <commit> <path> (<describe>)" or "-<commit> <path>" if not initialized
            line = result.stdout.strip()
            # Extract commit hash (first 40 chars after optional prefix)
            parts = line.split()
            if parts:
                commit = parts[0].lstrip('-+')[:40]
                return {
                    "commit": commit[:12],
                    "commit_full": commit,
                    "initialized": not line.startswith('-')
                }
        return {"commit": None, "commit_full": None, "initialized": False}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"commit": None, "commit_full": None, "initialized": False}


def get_package_version(package_name: str) -> Optional[str]:
    """Get installed package version."""
    try:
        import importlib.metadata
        return importlib.metadata.version(package_name)
    except Exception:
        return None


def get_gurobi_version() -> Optional[str]:
    """Get Gurobi version if available."""
    try:
        import gurobipy
        return f"{gurobipy.GRB.VERSION_MAJOR}.{gurobipy.GRB.VERSION_MINOR}.{gurobipy.GRB.VERSION_TECHNICAL}"
    except ImportError:
        return None


class ManifestGenerator:
    """Generates manifest.yaml for run traceability."""
    
    def __init__(
        self,
        run_name: str,
        run_type: str,
        config_path: "Path | List[Path]",
        scenario_path: Path,
        settings_path: Path,
        output_dir: Path,
        command: str
    ):
        self.run_name = run_name
        self.run_type = run_type
        # Handle single path or list of paths
        if isinstance(config_path, list):
            self.config_paths = [Path(p).resolve() for p in config_path]
        else:
            self.config_paths = [Path(config_path).resolve()]
        self.scenario_path = Path(scenario_path).resolve()
        self.settings_path = Path(settings_path).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.command = command
        self.timestamp = datetime.now(timezone.utc)
        
        # Determine repo root (for git info)
        self.repo_root = Path(__file__).parent.parent
    
    def generate(
        self,
        config: Any,  # MultiStageConfig
        results_summary: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate complete manifest dictionary.
        
        Parameters
        ----------
        config : MultiStageConfig
            The loaded configuration object
        results_summary : dict, optional
            Summary of run results (added after run completes)
        
        Returns
        -------
        dict
            Complete manifest
        """
        # Determine timeseries directory
        timeseries_dir = self.scenario_path.parent / "timeseries"
        if not timeseries_dir.exists():
            timeseries_dir = self.scenario_path.parent  # Fallback to scenario dir
        
        # Compute hashes for all timeseries files
        timeseries_files = {}
        if timeseries_dir.exists() and timeseries_dir.is_dir():
            for ts_file in sorted(timeseries_dir.glob("*.csv")):
                timeseries_files[ts_file.name] = compute_file_hash(ts_file)
        
        manifest = {
            "run": {
                "name": self.run_name,
                "type": self.run_type,
                "timestamp": self.timestamp.isoformat(),
                "command": self.command,
            },
            
            "inputs": {
                "configs": [
                    {"path": str(p), "sha256": compute_file_hash(p)}
                    for p in self.config_paths
                ],
                "scenario": {
                    "path": str(self.scenario_path),
                    "sha256": compute_file_hash(self.scenario_path),
                },
                "settings": {
                    "path": str(self.settings_path),
                    "sha256": compute_file_hash(self.settings_path),
                },
                "timeseries_dir": str(timeseries_dir),
                "timeseries_files": timeseries_files,
            },
            
            "parameters": {
                "stages": config.stages,
                "stage_duration_years": config.stage_duration_years,
                "wacc": config.wacc,
                "fleet_base": config.demand_base_num_vehicles,
                "growth_rate": config.demand_annual_growth_rate,
                "pv_base_cost": config.tech_costs.get('pv', {}).base_cost if 'pv' in config.tech_costs else None,
                "ess_base_cost": config.tech_costs.get('ess', {}).base_cost if 'ess' in config.tech_costs else None,
                "co2_base_limit_kg": config.emissions_base_limit_kg,
                "co2_final_limit_kg": config.emissions_final_limit_kg,
            },
            
            "git": get_git_info(self.repo_root),
            
            "revoletion": get_submodule_info(self.repo_root, "revoletion"),
            
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "gurobi": get_gurobi_version(),
                "oemof_solph": get_package_version("oemof.solph"),
                "pandas": get_package_version("pandas"),
            },
            
            "results": results_summary or {
                "status": "pending",
                "stages_completed": 0,
            }
        }
        
        return manifest
    
    def save(self, manifest: Dict[str, Any]) -> Path:
        """Save manifest to YAML file in output directory."""
        manifest_path = self.output_dir / "manifest.yaml"
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return manifest_path
    
    def update_results(self, manifest_path: Path, results_summary: Dict[str, Any]):
        """Update an existing manifest with results summary."""
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        manifest['results'] = results_summary
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def generate_run_name(
    config_path: Path,
    scenario_path: Path,
    run_type: str = "base"
) -> str:
    """
    Generate a default run name from config and scenario paths.
    
    Format: {date}_{type}_{depot}_{scenario}
    Example: 2026-01-07_base_schmid_test_50d
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Extract depot name from scenario path (e.g., inputs/schmid/scenarios/test_50d.csv -> schmid)
    # Try to find 'schmid', 'metzger', etc. in the path
    path_parts = scenario_path.parts
    depot_name = "unknown"
    for part in path_parts:
        if part in ["schmid", "metzger"]:
            depot_name = part
            break
    
    # Extract scenario name from filename
    scenario_name = scenario_path.stem
    # Remove common prefixes
    for prefix in ["scenarios_", "scenario_"]:
        if scenario_name.startswith(prefix):
            scenario_name = scenario_name[len(prefix):]
    
    return f"{date_str}_{run_type}_{depot_name}_{scenario_name}"
