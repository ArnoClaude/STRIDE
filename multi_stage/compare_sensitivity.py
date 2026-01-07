"""
Sensitivity analysis comparison and tornado diagram generation.

Compares results across multiple sensitivity runs and generates:
- Tornado diagram (parameter impact ranking)
- Spider/radar chart (multi-parameter comparison)
- Summary table

Usage:
    python -m multi_stage.compare_sensitivity outputs/sensitivity/schmid outputs/base/schmid/prod_180d
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional
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
    'figure.figsize': (8, 5),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Sensitivity parameter display names
PARAM_NAMES = {
    'wacc': 'WACC',
    'co2_factor': 'CO₂ Factor',
    'pv_capex': 'PV CAPEX',
    'ess_capex': 'ESS CAPEX',
}

# Colors
COLORS = {
    'low': '#56B4E9',   # Sky blue (favorable)
    'high': '#D55E00',  # Vermillion (unfavorable)
    'base': '#999999',  # Gray
}


def load_sensitivity_results(sensitivity_dir: Path, base_dir: Path) -> Dict:
    """Load results from all sensitivity runs and base case."""
    results = {}
    
    # Load base case
    base_results_path = base_dir / 'multi_stage_results.json'
    if base_results_path.exists():
        with open(base_results_path) as f:
            base_data = json.load(f)
        # Sum NPV across all stages
        results['base'] = {
            'npv_total': sum(stage.get('npv', 0) for stage in base_data.values()),
            'capex_total': sum(stage.get('capex_prj', 0) for stage in base_data.values()),
            'pv_final': max(stage.get('pv_size', 0) for stage in base_data.values()),
            'ess_final': max(stage.get('ess_size', 0) for stage in base_data.values()),
        }
    else:
        print(f"Warning: Base case not found at {base_results_path}")
        results['base'] = {'npv_total': 0, 'capex_total': 0, 'pv_final': 0, 'ess_final': 0}
    
    # Load each sensitivity case
    for case_dir in sensitivity_dir.iterdir():
        if case_dir.is_dir() and not case_dir.name.startswith('.'):
            results_path = case_dir / 'multi_stage_results.json'
            if results_path.exists():
                with open(results_path) as f:
                    data = json.load(f)
                results[case_dir.name] = {
                    'npv_total': sum(stage.get('npv', 0) for stage in data.values()),
                    'capex_total': sum(stage.get('capex_prj', 0) for stage in data.values()),
                    'pv_final': max(stage.get('pv_size', 0) for stage in data.values()),
                    'ess_final': max(stage.get('ess_size', 0) for stage in data.values()),
                }
    
    return results


def calculate_sensitivity_metrics(results: Dict) -> pd.DataFrame:
    """Calculate sensitivity metrics (swing, % change from base)."""
    base_npv = results['base']['npv_total']
    
    # Group by parameter
    params = set()
    for key in results.keys():
        if key != 'base':
            param = '_'.join(key.split('_')[:-1])  # e.g., 'wacc_low' -> 'wacc'
            params.add(param)
    
    metrics = []
    for param in params:
        low_key = f'{param}_low'
        high_key = f'{param}_high'
        
        low_npv = results.get(low_key, {}).get('npv_total', base_npv)
        high_npv = results.get(high_key, {}).get('npv_total', base_npv)
        
        swing = abs(high_npv - low_npv)
        pct_low = ((low_npv - base_npv) / abs(base_npv) * 100) if base_npv != 0 else 0
        pct_high = ((high_npv - base_npv) / abs(base_npv) * 100) if base_npv != 0 else 0
        
        metrics.append({
            'parameter': PARAM_NAMES.get(param, param),
            'param_key': param,
            'low_npv': low_npv,
            'base_npv': base_npv,
            'high_npv': high_npv,
            'swing': swing,
            'pct_change_low': pct_low,
            'pct_change_high': pct_high,
        })
    
    df = pd.DataFrame(metrics)
    df = df.sort_values('swing', ascending=False)
    return df


def plot_tornado(metrics: pd.DataFrame, output_path: Optional[Path] = None):
    """
    Generate tornado diagram showing parameter sensitivity ranked by impact.
    
    Horizontal bars show NPV deviation from base case.
    Parameters sorted by total swing (most impactful at top).
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    
    n_params = len(metrics)
    y_pos = np.arange(n_params)
    
    base_npv = metrics['base_npv'].iloc[0] / 1e6  # M€
    
    # Calculate deviations from base (in M€)
    low_dev = (metrics['low_npv'].values - metrics['base_npv'].values) / 1e6
    high_dev = (metrics['high_npv'].values - metrics['base_npv'].values) / 1e6
    
    # Plot bars
    # Low sensitivity (typically positive change = lower cost = better)
    bars_low = ax.barh(y_pos, low_dev, height=0.4, label='Low value', 
                       color=COLORS['low'], edgecolor='white', linewidth=0.5)
    # High sensitivity (typically negative change = higher cost = worse)
    bars_high = ax.barh(y_pos, high_dev, height=0.4, label='High value',
                        color=COLORS['high'], edgecolor='white', linewidth=0.5)
    
    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics['parameter'].values)
    ax.set_xlabel('Change in NPV from Base Case (M€)')
    ax.set_title(f'Tornado Diagram: Parameter Sensitivity\n(Base NPV: {base_npv:.2f} M€)')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.legend(loc='lower right', framealpha=0.9)
    
    # Add value labels
    for i, (low, high) in enumerate(zip(low_dev, high_dev)):
        if abs(low) > 0.01:
            ax.annotate(f'{low:+.2f}', (low, i), ha='right' if low < 0 else 'left',
                       va='center', fontsize=8, xytext=(-5 if low < 0 else 5, 0),
                       textcoords='offset points')
        if abs(high) > 0.01:
            ax.annotate(f'{high:+.2f}', (high, i), ha='right' if high < 0 else 'left',
                       va='center', fontsize=8, xytext=(-5 if high < 0 else 5, 0),
                       textcoords='offset points')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_sensitivity_table(metrics: pd.DataFrame, output_path: Optional[Path] = None):
    """Generate a formatted table of sensitivity results."""
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    for _, row in metrics.iterrows():
        table_data.append([
            row['parameter'],
            f"{row['low_npv']/1e6:.2f}",
            f"{row['base_npv']/1e6:.2f}",
            f"{row['high_npv']/1e6:.2f}",
            f"{row['swing']/1e6:.2f}",
            f"{row['pct_change_low']:+.1f}%",
            f"{row['pct_change_high']:+.1f}%",
        ])
    
    columns = ['Parameter', 'Low NPV', 'Base NPV', 'High NPV', 'Swing', '% Δ (Low)', '% Δ (High)']
    
    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        loc='center',
        cellLoc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Style header
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    plt.title('Sensitivity Analysis Summary (NPV in M€)', fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def generate_sensitivity_report(sensitivity_dir: Path, base_dir: Path, 
                                 output_dir: Optional[Path] = None):
    """Generate all sensitivity analysis visualizations and reports."""
    if output_dir is None:
        output_dir = sensitivity_dir / 'comparison'
    output_dir.mkdir(exist_ok=True)
    
    print(f"Loading results from: {sensitivity_dir}")
    print(f"Base case: {base_dir}")
    
    results = load_sensitivity_results(sensitivity_dir, base_dir)
    
    if len(results) < 2:
        print("Error: Need at least base case + 1 sensitivity run")
        return
    
    print(f"Loaded {len(results)} cases: {list(results.keys())}")
    
    metrics = calculate_sensitivity_metrics(results)
    
    # Generate plots
    for fmt in ['png', 'pdf']:
        plot_tornado(metrics, output_dir / f'tornado_diagram.{fmt}')
        plt.close()
        
        plot_sensitivity_table(metrics, output_dir / f'sensitivity_table.{fmt}')
        plt.close()
    
    # Save CSV
    metrics.to_csv(output_dir / 'sensitivity_metrics.csv', index=False)
    print(f"Saved: {output_dir / 'sensitivity_metrics.csv'}")
    
    print(f"\n✅ Sensitivity comparison complete. Results in: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare sensitivity analysis results and generate tornado diagram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m multi_stage.compare_sensitivity outputs/sensitivity/schmid outputs/base/schmid/prod_180d
  python -m multi_stage.compare_sensitivity outputs/sensitivity/schmid outputs/base/schmid/prod_180d -o figures/
        """
    )
    parser.add_argument('sensitivity_dir', type=Path, 
                        help='Directory containing sensitivity run folders')
    parser.add_argument('base_dir', type=Path,
                        help='Directory containing base case results')
    parser.add_argument('-o', '--output', type=Path, default=None,
                        help='Output directory for comparison plots')
    
    args = parser.parse_args()
    
    generate_sensitivity_report(args.sensitivity_dir, args.base_dir, args.output)


if __name__ == '__main__':
    main()
