"""
Thesis-quality visualizations for STRIDE multi-stage optimization results.

Generates publication-ready plots using matplotlib/seaborn with optional TikZ export.
Style: Clean, minimal, suitable for academic papers (Nature Energy style).
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from typing import Optional, Dict, Any
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
    'figure.figsize': (6, 4),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

# Color palette (colorblind-friendly)
COLORS = {
    'pv': '#E69F00',      # Orange
    'ess': '#56B4E9',     # Sky blue  
    'grid': '#009E73',    # Teal
    'capex': '#D55E00',   # Vermillion
    'opex': '#0072B2',    # Blue
    'npv': '#CC79A7',     # Pink
    'co2_limit': '#999999',  # Gray
    'co2_actual': '#F0E442',  # Yellow
}


def load_results(output_dir: Path) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Load multi-stage results from output directory."""
    timeline_path = output_dir / 'investment_timeline.csv'
    results_path = output_dir / 'multi_stage_results.json'
    
    timeline = pd.read_csv(timeline_path)
    with open(results_path) as f:
        results = json.load(f)
    
    return timeline, results


def plot_investment_timeline(timeline: pd.DataFrame, output_path: Optional[Path] = None):
    """
    Stacked bar chart of new investments per stage.
    Shows PV (kW), ESS (kWh scaled), Grid (kW scaled) additions.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    years = timeline['year'].values
    x = np.arange(len(years))
    width = 0.6
    
    # Scale values for visibility (PV in kW, ESS scaled up, grid in MW)
    pv_new = timeline['pv_new_kw'].values
    ess_new = timeline['ess_new_kwh'].values * 10  # Scale ESS for visibility
    
    # Stack bars
    bars_pv = ax.bar(x, pv_new, width, label='PV (kW)', color=COLORS['pv'], edgecolor='white', linewidth=0.5)
    bars_ess = ax.bar(x, ess_new, width, bottom=pv_new, label='ESS (kWh × 10)', color=COLORS['ess'], edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Investment Stage')
    ax.set_ylabel('New Capacity (kW / scaled kWh)')
    ax.set_title('Investment Deferral: Technology Additions per Stage')
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Add value labels on bars
    for i, (pv, ess) in enumerate(zip(timeline['pv_new_kw'], timeline['ess_new_kwh'])):
        if pv > 50:
            ax.annotate(f'{pv:.0f}', (i, pv/2), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        if ess > 0.5:
            ax.annotate(f'{ess:.0f}', (i, pv + ess*5), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_cumulative_capacity(timeline: pd.DataFrame, output_path: Optional[Path] = None):
    """
    Line chart showing cumulative capacity evolution over time.
    Key plot for showing investment deferral strategy.
    """
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    
    years = timeline['year'].values
    
    # PV on primary axis (MW)
    pv_mw = timeline['pv_total_kw'].values / 1000
    line_pv, = ax1.plot(years, pv_mw, 'o-', color=COLORS['pv'], linewidth=2, markersize=8, label='PV Capacity')
    ax1.fill_between(years, 0, pv_mw, alpha=0.2, color=COLORS['pv'])
    ax1.set_xlabel('Year')
    ax1.set_ylabel('PV Capacity (MW)', color=COLORS['pv'])
    ax1.tick_params(axis='y', labelcolor=COLORS['pv'])
    ax1.set_ylim(0, max(pv_mw) * 1.15)
    
    # ESS on secondary axis (kWh) - only if significant
    ax2 = ax1.twinx()
    ess_kwh = timeline['ess_total_kwh'].values
    if max(ess_kwh) > 1:
        line_ess, = ax2.plot(years, ess_kwh, 's--', color=COLORS['ess'], linewidth=2, markersize=8, label='ESS Capacity')
        ax2.set_ylabel('ESS Capacity (kWh)', color=COLORS['ess'])
        ax2.tick_params(axis='y', labelcolor=COLORS['ess'])
        ax2.set_ylim(0, max(ess_kwh) * 1.15)
        lines = [line_pv, line_ess]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.9)
    else:
        ax2.set_visible(False)
        ax1.legend(loc='upper left', framealpha=0.9)
    
    ax1.set_title('Cumulative Infrastructure Capacity Over Planning Horizon')
    
    # Add annotations for key investment years
    for i, (year, pv) in enumerate(zip(years, pv_mw)):
        if i > 0 and (pv - pv_mw[i-1]) > 0.3:  # Significant addition
            ax1.annotate(f'+{(pv - pv_mw[i-1])*1000:.0f} kW', 
                        (year, pv), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontsize=8,
                        color=COLORS['pv'])
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax1


def plot_cost_breakdown(timeline: pd.DataFrame, results: Dict, output_path: Optional[Path] = None):
    """
    Stacked bar chart of CAPEX and NPV by stage.
    Shows economic progression over planning horizon.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    years = timeline['year'].values
    x = np.arange(len(years))
    width = 0.35
    
    # Get CAPEX and OPEX from results
    capex = np.array([results[str(y)]['capex_prj'] for y in years]) / 1e6  # M€
    npv = np.array([results[str(y)]['npv'] for y in years]) / 1e6  # M€
    npv_disc = timeline['npv_discounted'].values / 1e6  # M€
    
    # Bar charts
    bars1 = ax.bar(x - width/2, capex, width, label='CAPEX', color=COLORS['capex'], edgecolor='white')
    bars2 = ax.bar(x + width/2, -npv_disc, width, label='NPV (discounted, inverted)', color=COLORS['npv'], edgecolor='white')
    
    ax.set_xlabel('Investment Stage')
    ax.set_ylabel('Cost (M€)')
    ax.set_title('Cost Evolution Across Planning Stages')
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.axhline(y=0, color='black', linewidth=0.5)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_npv_waterfall(timeline: pd.DataFrame, results: Dict, output_path: Optional[Path] = None):
    """
    Waterfall chart showing cumulative discounted NPV.
    Demonstrates total project economics.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    years = timeline['year'].values
    npv_disc = timeline['npv_discounted'].values / 1e6  # M€
    
    # Calculate cumulative
    cumulative = np.cumsum(npv_disc)
    
    # Waterfall bars
    x = np.arange(len(years) + 1)
    widths = 0.6
    
    # Starting point
    starts = np.zeros(len(years))
    starts[0] = 0
    starts[1:] = cumulative[:-1]
    
    colors = [COLORS['npv'] if v < 0 else COLORS['grid'] for v in npv_disc]
    
    # Draw bars
    for i, (start, height) in enumerate(zip(starts, npv_disc)):
        ax.bar(i, height, widths, bottom=start, color=colors[i], edgecolor='white', linewidth=0.5)
        # Connector lines
        if i < len(years) - 1:
            ax.plot([i + widths/2, i + 1 - widths/2], [start + height, start + height], 
                   'k-', linewidth=0.5, alpha=0.5)
    
    # Total bar
    ax.bar(len(years), cumulative[-1], widths, color='#333333', edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Investment Stage')
    ax.set_ylabel('NPV (M€, discounted)')
    ax.set_title('Cumulative NPV Waterfall: Multi-Stage Investment')
    ax.set_xticks(x)
    ax.set_xticklabels(list(years) + ['Total'])
    ax.axhline(y=0, color='black', linewidth=0.5)
    
    # Add value annotations
    for i, (val, cum) in enumerate(zip(npv_disc, cumulative)):
        ax.annotate(f'{val:.1f}', (i, cum - val/2), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    ax.annotate(f'{cumulative[-1]:.1f}', (len(years), cumulative[-1]/2), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_technology_cost_decline(years: list, output_path: Optional[Path] = None):
    """
    Line chart showing assumed technology cost decline over time.
    Contextualizes investment deferral rationale.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    base_year = years[0]
    year_array = np.array(years)
    years_from_base = year_array - base_year
    
    # Cost decline assumptions (from config)
    pv_base = 1.0  # €/W
    pv_decline = 0.03  # 3%/yr
    ess_base = 0.50  # €/Wh
    ess_decline = 0.05  # 5%/yr
    
    pv_cost = pv_base * (1 - pv_decline) ** years_from_base
    ess_cost = ess_base * (1 - ess_decline) ** years_from_base
    
    ax.plot(year_array, pv_cost, 'o-', color=COLORS['pv'], linewidth=2, markersize=8, label='PV (€/W)')
    ax.plot(year_array, ess_cost, 's-', color=COLORS['ess'], linewidth=2, markersize=8, label='ESS (€/Wh)')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Specific Cost (€/W or €/Wh)')
    ax.set_title('Technology Cost Decline Assumptions')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_ylim(0, 1.1)
    
    # Add percentage labels
    for i, (y, pv, ess) in enumerate(zip(year_array, pv_cost, ess_cost)):
        if i > 0:
            pv_reduction = (1 - pv/pv_cost[0]) * 100
            ax.annotate(f'-{pv_reduction:.0f}%', (y, pv), textcoords="offset points", 
                       xytext=(10, 0), ha='left', fontsize=8, color=COLORS['pv'])
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_co2_compliance(results: Dict, co2_limits: Optional[Dict] = None, output_path: Optional[Path] = None):
    """
    Bar chart comparing CO2 emissions vs limits per stage.
    Shows environmental compliance trajectory.
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    years = sorted([int(y) for y in results.keys()])
    x = np.arange(len(years))
    width = 0.35
    
    # Get CO2 from results (extrapolated to project duration)
    co2_actual = np.array([results[str(y)]['co2_prj_kg'] for y in years]) / 1000  # tons
    
    # Default CO2 limits if not provided (from config: 200k→20k kg linear)
    if co2_limits is None:
        co2_limits = {2025: 200000, 2030: 164000, 2035: 128000, 2040: 92000, 2045: 56000, 2050: 20000}
    co2_limit = np.array([co2_limits.get(y, 100000) for y in years]) / 1000  # tons
    
    bars1 = ax.bar(x - width/2, co2_actual, width, label='Actual Emissions', color=COLORS['co2_actual'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, co2_limit, width, label='CO₂ Limit', color=COLORS['co2_limit'], edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Investment Stage')
    ax.set_ylabel('CO₂ Emissions (tons/project period)')
    ax.set_title('CO₂ Compliance: Emissions vs Regulatory Limits')
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.legend(loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def plot_fleet_growth(results: Dict, output_path: Optional[Path] = None):
    """
    Simple line chart showing fleet size evolution.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    years = sorted([int(y) for y in results.keys()])
    
    # Extract fleet size from grid capacity as proxy (or use known values)
    # Fleet: 84 vehicles in 2025, 2% growth per year
    base_fleet = 84
    growth_rate = 0.02
    fleet_sizes = [int(base_fleet * (1 + growth_rate) ** ((y - 2025) / 5) ** 5) for y in years]
    # Use actual values from session notes
    fleet_actual = [84, 92, 102, 113, 124, 137][:len(years)]
    
    ax.plot(years, fleet_actual, 'o-', color='#333333', linewidth=2, markersize=10)
    ax.fill_between(years, 0, fleet_actual, alpha=0.1, color='#333333')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Fleet Size (vehicles)')
    ax.set_title('Fleet Growth Over Planning Horizon')
    ax.set_ylim(0, max(fleet_actual) * 1.15)
    
    for y, f in zip(years, fleet_actual):
        ax.annotate(str(f), (y, f), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
        print(f"Saved: {output_path}")
    return fig, ax


def generate_all_plots(output_dir: Path, plot_dir: Optional[Path] = None, 
                       png: bool = True, pdf: bool = True, latex: bool = False):
    """Generate all thesis plots from results."""
    timeline, results = load_results(output_dir)
    
    if plot_dir is None:
        plot_dir = output_dir / 'plots'
    plot_dir.mkdir(exist_ok=True)
    
    formats = []
    if png: formats.append('png')
    if pdf: formats.append('pdf')
    
    print(f"Generating plots in: {plot_dir}")
    print(f"Formats: {', '.join(formats)}" + (" + LaTeX/TikZ" if latex else ""))
    
    years = [int(y) for y in results.keys()]
    
    # Plot functions with their names
    plot_specs = [
        ('investment_timeline', lambda p: plot_investment_timeline(timeline, p)),
        ('cumulative_capacity', lambda p: plot_cumulative_capacity(timeline, p)),
        ('cost_breakdown', lambda p: plot_cost_breakdown(timeline, results, p)),
        ('npv_waterfall', lambda p: plot_npv_waterfall(timeline, results, p)),
        ('cost_decline', lambda p: plot_technology_cost_decline(sorted(years), p)),
        ('co2_compliance', lambda p: plot_co2_compliance(results, output_path=p)),
        ('fleet_growth', lambda p: plot_fleet_growth(results, p)),
    ]
    
    count = 0
    for name, plot_func in plot_specs:
        for fmt in formats:
            plot_func(plot_dir / f'{name}.{fmt}')
            plt.close('all')
            count += 1
    
    print(f"\n✅ Generated {count} plots in {plot_dir}")
    
    # TikZ/LaTeX export
    if latex:
        try:
            import tikzplotlib
            print("\nExporting TikZ versions for LaTeX...")
            for name, plot_func in plot_specs:
                fig, _ = plot_func(None)  # Generate without saving
                tikzplotlib.save(plot_dir / f'{name}.tex')
                plt.close(fig)
            print(f"✅ TikZ export complete ({len(plot_specs)} files)")
        except ImportError:
            print("\n⚠️  tikzplotlib not installed. Run 'pip install tikzplotlib' for LaTeX export.")


def main():
    parser = argparse.ArgumentParser(
        description='Generate thesis visualizations from STRIDE results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m multi_stage.visualize outputs/schmid_6stage --png
  python -m multi_stage.visualize outputs/schmid_6stage --pdf --latex
  python -m multi_stage.visualize outputs/schmid_6stage --all
        """
    )
    parser.add_argument('output_dir', type=Path, help='Path to multi-stage output directory')
    parser.add_argument('--plot-dir', type=Path, default=None, help='Output directory for plots (default: <output_dir>/plots)')
    parser.add_argument('--png', action='store_true', help='Generate PNG plots (raster, 300 DPI)')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF plots (vector graphics)')
    parser.add_argument('--latex', action='store_true', help='Generate LaTeX/TikZ plots (requires tikzplotlib)')
    parser.add_argument('--all', action='store_true', help='Generate all formats (PNG + PDF + LaTeX)')
    args = parser.parse_args()
    
    # Default to PNG if no format specified
    if not any([args.png, args.pdf, args.latex, args.all]):
        args.png = True
        args.pdf = True
    
    if args.all:
        args.png = args.pdf = args.latex = True
    
    generate_all_plots(
        args.output_dir, 
        args.plot_dir,
        png=args.png,
        pdf=args.pdf,
        latex=args.latex
    )


if __name__ == '__main__':
    main()
