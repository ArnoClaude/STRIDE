"""
Run comparison visualizations for STRIDE multi-stage optimization.

Generates thesis-quality plots comparing:
- Base case vs sensitivity pairs (pairwise)
- All runs overview (tornado, summary)
- Investment trajectory comparisons

Usage:
    python -m multi_stage.compare runs/schmid/base runs/schmid/sensitivity -o runs/schmid/comparison
    python -m multi_stage.compare runs/schmid/base runs/schmid/sensitivity/co2_low runs/schmid/sensitivity/co2_high --pair
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# Publication-quality settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

# Color palette - subtle, professional, colorblind-friendly
COLORS = {
    # Base case
    'base': '#2C3E50',      # Dark blue-gray
    
    # Sensitivity pairs (muted, not alarming)
    'low': '#27AE60',       # Muted green (favorable)
    'high': '#E67E22',      # Muted orange (unfavorable)
    
    # Technology colors (consistent with visualize.py)
    'pv': '#E69F00',        # Orange
    'ess': '#56B4E9',       # Sky blue
    'grid': '#009E73',      # Teal
    
    # Financial
    'npv': '#8E44AD',       # Purple
    'capex': '#C0392B',     # Dark red
    
    # Neutral
    'gray': '#7F8C8D',
}

# Parameter display names
PARAM_DISPLAY = {
    'co2': 'CO₂ Limit',
    'pv_capex': 'PV CAPEX',
    'ess_capex': 'ESS CAPEX',
    'wacc': 'WACC',
    'fleet_growth': 'Fleet Growth',
}


def load_run_results(run_dir: Path) -> Tuple[pd.DataFrame, Dict]:
    """Load results from a single run directory."""
    timeline_path = run_dir / 'investment_timeline.csv'
    results_path = run_dir / 'multi_stage_results.json'
    
    if not timeline_path.exists() or not results_path.exists():
        raise FileNotFoundError(f"Results not found in {run_dir}")
    
    timeline = pd.read_csv(timeline_path)
    with open(results_path) as f:
        results = json.load(f)
    
    return timeline, results


def load_all_sensitivity_runs(base_dir: Path, sensitivity_dir: Path) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
    """Load base case and all sensitivity runs."""
    runs = {}
    
    # Load base case
    runs['base'] = load_run_results(base_dir)
    
    # Load sensitivity runs
    for case_dir in sensitivity_dir.iterdir():
        if case_dir.is_dir() and not case_dir.name.startswith('.'):
            try:
                runs[case_dir.name] = load_run_results(case_dir)
            except FileNotFoundError:
                print(f"  Skipping {case_dir.name} (no results)")
    
    return runs


def extract_summary_metrics(timeline: pd.DataFrame, results: Dict) -> Dict:
    """Extract key summary metrics from run results."""
    years = sorted([int(y) for y in results.keys()])
    final_year = str(max(years))
    
    return {
        'npv_total': sum(results[str(y)].get('npv', 0) for y in years),
        'capex_total': sum(results[str(y)].get('capex_prj', 0) for y in years),
        'pv_final_kw': results[final_year].get('pv_size', 0),
        'ess_final_kwh': results[final_year].get('ess_size', 0),
        'grid_final_kw': results[final_year].get('grid_size', 0),
        'co2_total_kg': sum(results[str(y)].get('co2_sim_kg', 0) or 0 for y in years),
        'years': years,
    }


# =============================================================================
# TORNADO DIAGRAMS
# =============================================================================

def plot_tornado_npv(runs: Dict, output_path: Optional[Path] = None):
    """
    Tornado diagram showing NPV sensitivity to each parameter.
    
    Horizontal bars showing deviation from base case NPV.
    Sorted by total swing (most impactful at top).
    """
    base_timeline, base_results = runs['base']
    base_metrics = extract_summary_metrics(base_timeline, base_results)
    base_npv = base_metrics['npv_total']
    
    # Group sensitivity runs by parameter
    params = {}
    for name, (timeline, results) in runs.items():
        if name == 'base':
            continue
        # Parse parameter name: e.g., 'co2_low' -> param='co2', variant='low'
        parts = name.rsplit('_', 1)
        if len(parts) == 2 and parts[1] in ('low', 'high'):
            param, variant = parts
            if param not in params:
                params[param] = {}
            metrics = extract_summary_metrics(timeline, results)
            params[param][variant] = metrics['npv_total']
    
    # Calculate deviations and sort by swing
    data = []
    for param, variants in params.items():
        low_npv = variants.get('low', base_npv)
        high_npv = variants.get('high', base_npv)
        swing = abs(high_npv - low_npv)
        data.append({
            'param': param,
            'display': PARAM_DISPLAY.get(param, param),
            'low_dev': (low_npv - base_npv) / 1e6,
            'high_dev': (high_npv - base_npv) / 1e6,
            'swing': swing / 1e6,
        })
    
    df = pd.DataFrame(data).sort_values('swing', ascending=True)  # Ascending for bottom-to-top
    
    # Plot
    fig, ax = plt.subplots(figsize=(9, 0.8 * len(df) + 2))
    
    y_pos = np.arange(len(df))
    
    ax.barh(y_pos - 0.15, df['low_dev'], height=0.3, label='Low', 
            color=COLORS['low'], edgecolor='white', linewidth=0.5)
    ax.barh(y_pos + 0.15, df['high_dev'], height=0.3, label='High',
            color=COLORS['high'], edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['display'])
    ax.set_xlabel('Change in Total NPV from Base Case (M€)')
    ax.set_title(f'NPV Sensitivity Analysis\nBase Case NPV: {base_npv/1e6:.2f} M€')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.legend(loc='lower right', framealpha=0.9)
    
    # Value labels
    for i, row in df.reset_index(drop=True).iterrows():
        if abs(row['low_dev']) > 0.01:
            ha = 'right' if row['low_dev'] < 0 else 'left'
            offset = -5 if row['low_dev'] < 0 else 5
            ax.annotate(f"{row['low_dev']:+.2f}", (row['low_dev'], i - 0.15),
                       ha=ha, va='center', fontsize=8, 
                       xytext=(offset, 0), textcoords='offset points')
        if abs(row['high_dev']) > 0.01:
            ha = 'right' if row['high_dev'] < 0 else 'left'
            offset = -5 if row['high_dev'] < 0 else 5
            ax.annotate(f"{row['high_dev']:+.2f}", (row['high_dev'], i + 0.15),
                       ha=ha, va='center', fontsize=8,
                       xytext=(offset, 0), textcoords='offset points')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_tornado_capex(runs: Dict, output_path: Optional[Path] = None):
    """Tornado diagram for total CAPEX sensitivity."""
    base_timeline, base_results = runs['base']
    base_metrics = extract_summary_metrics(base_timeline, base_results)
    base_capex = base_metrics['capex_total']
    
    params = {}
    for name, (timeline, results) in runs.items():
        if name == 'base':
            continue
        parts = name.rsplit('_', 1)
        if len(parts) == 2 and parts[1] in ('low', 'high'):
            param, variant = parts
            if param not in params:
                params[param] = {}
            metrics = extract_summary_metrics(timeline, results)
            params[param][variant] = metrics['capex_total']
    
    data = []
    for param, variants in params.items():
        low_val = variants.get('low', base_capex)
        high_val = variants.get('high', base_capex)
        swing = abs(high_val - low_val)
        data.append({
            'param': param,
            'display': PARAM_DISPLAY.get(param, param),
            'low_dev': (low_val - base_capex) / 1e6,
            'high_dev': (high_val - base_capex) / 1e6,
            'swing': swing / 1e6,
        })
    
    df = pd.DataFrame(data).sort_values('swing', ascending=True)
    
    fig, ax = plt.subplots(figsize=(9, 0.8 * len(df) + 2))
    
    y_pos = np.arange(len(df))
    
    ax.barh(y_pos - 0.15, df['low_dev'], height=0.3, label='Low',
            color=COLORS['low'], edgecolor='white', linewidth=0.5)
    ax.barh(y_pos + 0.15, df['high_dev'], height=0.3, label='High',
            color=COLORS['high'], edgecolor='white', linewidth=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['display'])
    ax.set_xlabel('Change in Total CAPEX from Base Case (M€)')
    ax.set_title(f'CAPEX Sensitivity Analysis\nBase Case CAPEX: {base_capex/1e6:.2f} M€')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.legend(loc='lower right', framealpha=0.9)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


# =============================================================================
# INVESTMENT TRAJECTORY COMPARISONS
# =============================================================================

def plot_trajectory_comparison(runs: Dict, metric: str, 
                               output_path: Optional[Path] = None,
                               absolute: bool = True):
    """
    Line plot comparing investment trajectories across all runs.
    
    Args:
        runs: Dict of run name -> (timeline, results)
        metric: 'pv', 'ess', or 'grid'
        absolute: If True, show absolute values. If False, show % of base final.
    """
    metric_cols = {
        'pv': ('pv_total_kw', 'PV Capacity', 'kWp'),
        'ess': ('ess_total_kwh', 'ESS Capacity', 'kWh'),
        'grid': ('grid_total_kw', 'Grid Capacity', 'kW'),
    }
    
    col, title, unit = metric_cols[metric]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    base_timeline, base_results = runs['base']
    years = base_timeline['year'].values
    base_values = get_trajectory_values(base_timeline, base_results, col)
    base_final = base_values[-1] if base_values[-1] != 0 else 1
    
    # Plot base case prominently
    plot_values = base_values if absolute else base_values / base_final * 100
    ax.plot(years, plot_values, 'o-', color=COLORS['base'], linewidth=2.5, 
            markersize=8, label='Base', zorder=10)
    
    # Plot sensitivity runs
    for name, (timeline, results) in runs.items():
        if name == 'base':
            continue
        values = get_trajectory_values(timeline, results, col)
        if not absolute:
            values = values / base_final * 100
        
        # Determine color based on low/high
        if name.endswith('_low'):
            color = COLORS['low']
            alpha = 0.7
        elif name.endswith('_high'):
            color = COLORS['high']
            alpha = 0.7
        else:
            color = COLORS['gray']
            alpha = 0.5
        
        label = PARAM_DISPLAY.get(name.rsplit('_', 1)[0], name)
        if name.endswith('_low'):
            label += ' (low)'
        elif name.endswith('_high'):
            label += ' (high)'
        
        ax.plot(years, values, 's--', color=color, linewidth=1.5,
                markersize=5, alpha=alpha, label=label)
    
    ax.set_xlabel('Year')
    if absolute:
        ax.set_ylabel(f'{title} ({unit})')
    else:
        ax.set_ylabel(f'{title} (% of Base 2050)')
    ax.set_title(f'{title} Trajectory Comparison')
    ax.legend(loc='upper left', framealpha=0.9, fontsize=8)
    ax.set_xticks(years)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def get_trajectory_values(timeline: pd.DataFrame, results: Dict, col: str) -> np.ndarray:
    """Extract trajectory values, falling back to results JSON if column missing from timeline."""
    if col in timeline.columns:
        return timeline[col].values
    
    # Fallback: extract from results JSON
    years = sorted([int(y) for y in results.keys()])
    json_key_map = {
        'pv_total_kw': 'pv_size_total',
        'ess_total_kwh': 'ess_size_total',
        'grid_total_kw': 'grid_size_total',
    }
    json_key = json_key_map.get(col, col)
    return np.array([results[str(y)].get(json_key, 0) or 0 for y in years])


def plot_pairwise_trajectory(base_run: Tuple, low_run: Tuple, high_run: Tuple,
                              param_name: str, output_path: Optional[Path] = None):
    """
    Three-line plot: Base vs Low vs High for a single sensitivity parameter.
    Shows PV, ESS, Grid in subplots.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    
    metrics = [
        ('pv_total_kw', 'PV Capacity (kWp)', COLORS['pv']),
        ('ess_total_kwh', 'ESS Capacity (kWh)', COLORS['ess']),
        ('grid_total_kw', 'Grid Capacity (kW)', COLORS['grid']),
    ]
    
    base_timeline, base_results = base_run
    low_timeline, low_results = low_run
    high_timeline, high_results = high_run
    years = base_timeline['year'].values
    
    for ax, (col, ylabel, _) in zip(axes, metrics):
        base_vals = get_trajectory_values(base_timeline, base_results, col)
        low_vals = get_trajectory_values(low_timeline, low_results, col)
        high_vals = get_trajectory_values(high_timeline, high_results, col)
        
        ax.plot(years, base_vals, 'o-', color=COLORS['base'], 
                linewidth=2, markersize=7, label='Base')
        ax.plot(years, low_vals, 's--', color=COLORS['low'],
                linewidth=1.5, markersize=5, label='Low')
        ax.plot(years, high_vals, '^--', color=COLORS['high'],
                linewidth=1.5, markersize=5, label='High')
        
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_xticks(years)
        ax.legend(loc='upper left', fontsize=8)
    
    display_name = PARAM_DISPLAY.get(param_name, param_name)
    fig.suptitle(f'Investment Trajectory: {display_name} Sensitivity', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, axes


def plot_pairwise_trajectory_percent(base_run: Tuple, low_run: Tuple, high_run: Tuple,
                                      param_name: str, output_path: Optional[Path] = None):
    """Same as pairwise_trajectory but showing % of base final value."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    
    metrics = [
        ('pv_total_kw', 'PV (% of Base 2050)', COLORS['pv']),
        ('ess_total_kwh', 'ESS (% of Base 2050)', COLORS['ess']),
        ('grid_total_kw', 'Grid (% of Base 2050)', COLORS['grid']),
    ]
    
    base_timeline, base_results = base_run
    low_timeline, low_results = low_run
    high_timeline, high_results = high_run
    years = base_timeline['year'].values
    
    for ax, (col, ylabel, _) in zip(axes, metrics):
        base_vals = get_trajectory_values(base_timeline, base_results, col)
        low_vals = get_trajectory_values(low_timeline, low_results, col)
        high_vals = get_trajectory_values(high_timeline, high_results, col)
        
        base_final = base_vals[-1] if base_vals[-1] != 0 else 1  # Avoid division by zero
        
        ax.plot(years, base_vals / base_final * 100, 'o-', 
                color=COLORS['base'], linewidth=2, markersize=7, label='Base')
        ax.plot(years, low_vals / base_final * 100, 's--',
                color=COLORS['low'], linewidth=1.5, markersize=5, label='Low')
        ax.plot(years, high_vals / base_final * 100, '^--',
                color=COLORS['high'], linewidth=1.5, markersize=5, label='High')
        
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_xticks(years)
        ax.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
        ax.legend(loc='upper left', fontsize=8)
    
    display_name = PARAM_DISPLAY.get(param_name, param_name)
    fig.suptitle(f'Investment Trajectory (Normalized): {display_name} Sensitivity', 
                 fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, axes


# =============================================================================
# SUMMARY TABLE
# =============================================================================

def generate_summary_table(runs: Dict, output_path: Optional[Path] = None) -> pd.DataFrame:
    """Generate summary table of all runs."""
    rows = []
    
    for name, (timeline, results) in runs.items():
        metrics = extract_summary_metrics(timeline, results)
        rows.append({
            'Run': name,
            'NPV Total (M€)': metrics['npv_total'] / 1e6,
            'CAPEX Total (M€)': metrics['capex_total'] / 1e6,
            'PV 2050 (kWp)': metrics['pv_final_kw'],
            'ESS 2050 (kWh)': metrics['ess_final_kwh'],
            'Grid 2050 (kW)': metrics['grid_final_kw'],
            'CO₂ Total (t)': metrics['co2_total_kg'] / 1000,
        })
    
    df = pd.DataFrame(rows)
    
    if output_path:
        df.to_csv(output_path, index=False, float_format='%.2f')
        print(f"Saved: {output_path}")
    
    return df


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def generate_all_comparisons(base_dir: Path, sensitivity_dir: Path, 
                              output_dir: Path, formats: List[str] = ['png', 'pdf']):
    """Generate all comparison visualizations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading runs...")
    print(f"  Base: {base_dir}")
    print(f"  Sensitivity: {sensitivity_dir}")
    
    runs = load_all_sensitivity_runs(base_dir, sensitivity_dir)
    print(f"  Loaded {len(runs)} runs: {list(runs.keys())}")
    
    if len(runs) < 2:
        print("Error: Need at least base case + 1 sensitivity run")
        return
    
    count = 0
    
    # Tornado diagrams
    print("\nGenerating tornado diagrams...")
    for fmt in formats:
        plot_tornado_npv(runs, output_dir / f'tornado_npv.{fmt}')
        plot_tornado_capex(runs, output_dir / f'tornado_capex.{fmt}')
        plt.close('all')
        count += 2
    
    # All-runs trajectory comparison
    print("Generating trajectory comparisons (all runs)...")
    for metric in ['pv', 'ess', 'grid']:
        for fmt in formats:
            plot_trajectory_comparison(runs, metric, 
                                       output_dir / f'trajectory_{metric}_all.{fmt}',
                                       absolute=True)
            plot_trajectory_comparison(runs, metric,
                                       output_dir / f'trajectory_{metric}_all_pct.{fmt}',
                                       absolute=False)
            plt.close('all')
            count += 2
    
    # Pairwise comparisons
    print("Generating pairwise comparisons...")
    params_found = set()
    for name in runs.keys():
        if name != 'base' and name.endswith(('_low', '_high')):
            param = name.rsplit('_', 1)[0]
            params_found.add(param)
    
    for param in params_found:
        low_name = f'{param}_low'
        high_name = f'{param}_high'
        
        if low_name in runs and high_name in runs:
            for fmt in formats:
                plot_pairwise_trajectory(runs['base'], runs[low_name], runs[high_name],
                                         param, output_dir / f'trajectory_{param}.{fmt}')
                plot_pairwise_trajectory_percent(runs['base'], runs[low_name], runs[high_name],
                                                  param, output_dir / f'trajectory_{param}_pct.{fmt}')
                plt.close('all')
                count += 2
    
    # Summary table
    print("Generating summary table...")
    generate_summary_table(runs, output_dir / 'summary_table.csv')
    count += 1
    
    print(f"\n✅ Generated {count} files in {output_dir}")


def generate_pairwise_comparison(base_dir: Path, low_dir: Path, high_dir: Path,
                                  param_name: str, output_dir: Path,
                                  formats: List[str] = ['png', 'pdf']):
    """Generate comparison plots for a single sensitivity parameter."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading runs for {param_name} comparison...")
    print(f"  Base: {base_dir}")
    print(f"  Low:  {low_dir}")
    print(f"  High: {high_dir}")
    
    try:
        base_run = load_run_results(base_dir)
        low_run = load_run_results(low_dir)
        high_run = load_run_results(high_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    count = 0
    
    # Pairwise trajectory plots
    for fmt in formats:
        plot_pairwise_trajectory(base_run, low_run, high_run, param_name,
                                  output_dir / f'trajectory_{param_name}.{fmt}')
        plot_pairwise_trajectory_percent(base_run, low_run, high_run, param_name,
                                          output_dir / f'trajectory_{param_name}_pct.{fmt}')
        plt.close('all')
        count += 2
    
    # Summary table for just these 3 runs
    runs = {
        'base': base_run,
        f'{param_name}_low': low_run,
        f'{param_name}_high': high_run,
    }
    generate_summary_table(runs, output_dir / f'summary_{param_name}.csv')
    count += 1
    
    print(f"\n✅ Generated {count} files in {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare STRIDE optimization runs and generate visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare base vs all sensitivity runs
  python -m multi_stage.compare runs/schmid/base runs/schmid/sensitivity -o runs/schmid/comparison
  
  # Compare single parameter (pairwise: base vs low vs high)
  python -m multi_stage.compare runs/schmid/base runs/schmid/sensitivity/co2_low runs/schmid/sensitivity/co2_high --pair co2 -o runs/schmid/comparison
  
  # Generate only PDF (for LaTeX)
  python -m multi_stage.compare runs/schmid/base runs/schmid/sensitivity -o runs/schmid/comparison --pdf-only
        """
    )
    parser.add_argument('base_dir', type=Path, help='Path to base case run directory')
    parser.add_argument('sensitivity_dir', type=Path, 
                        help='Path to sensitivity runs directory (or low_dir if --pair)')
    parser.add_argument('high_dir', type=Path, nargs='?', default=None,
                        help='Path to high sensitivity run (only with --pair)')
    parser.add_argument('--pair', type=str, metavar='PARAM_NAME',
                        help='Single parameter comparison mode. Provide param name (e.g., co2, pv_capex)')
    parser.add_argument('-o', '--output', type=Path, default=None,
                        help='Output directory for comparison plots')
    parser.add_argument('--pdf-only', action='store_true', help='Generate only PDF (vector)')
    parser.add_argument('--png-only', action='store_true', help='Generate only PNG (raster)')
    
    args = parser.parse_args()
    
    formats = ['png', 'pdf']
    if args.pdf_only:
        formats = ['pdf']
    elif args.png_only:
        formats = ['png']
    
    if args.pair:
        # Pairwise mode: base_dir, low_dir, high_dir
        if args.high_dir is None:
            parser.error("--pair requires 3 directories: base_dir low_dir high_dir")
        
        output_dir = args.output or args.base_dir.parent / 'comparison'
        generate_pairwise_comparison(
            args.base_dir, 
            args.sensitivity_dir,  # This is low_dir in pair mode
            args.high_dir,
            args.pair,
            output_dir,
            formats
        )
    else:
        # Full comparison mode
        output_dir = args.output or args.sensitivity_dir / 'comparison'
        generate_all_comparisons(args.base_dir, args.sensitivity_dir, output_dir, formats)


if __name__ == '__main__':
    main()
