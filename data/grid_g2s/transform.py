#!/usr/bin/env python3
"""
Transform SMARD wholesale electricity prices to REVOL-E-TION grid opex format.

Input:  SMARD CSV export (Großhandelspreise, DE/LU, hourly)
Output: grid_opex_g2s_YYYY.csv with columns [time, cost] in €/Wh

Usage:
    python transform.py                          # Process all raw files
    python transform.py --year 2025              # Process specific year
    python transform.py --year 2025 --scale 0.95 # Apply price scaling factor
"""

import argparse
from pathlib import Path
import pandas as pd

# Retail markup components (€/Wh) for Bavarian freight depot
# Based on Bayernwerk Netzentgelte 2025 + netztransparenz.de surcharges 2025
#
# Network fees (Bayernwerk Preisblatt LG JLP 2025, Niederspannung <2500 Bh):
#   - Arbeitspreis: 7.45 ct/kWh
#   - (Leistungspreis 21.93 €/kW/a modeled separately via peakshaving)
#
# Surcharges (netztransparenz.de, 2025):
#   - KWKG-Umlage: 0.277 ct/kWh
#   - Offshore-Netzumlage: 0.816 ct/kWh
#   - §19 StromNEV (≤1 GWh/a): 1.558 ct/kWh
#   - Subtotal: 2.651 ct/kWh
#
# Taxes & fees:
#   - Stromsteuer: 2.05 ct/kWh
#   - Konzessionsabgabe (Sondervertrag): 0.11 ct/kWh
#   - Subtotal: 2.16 ct/kWh
#
# Total retail markup: 7.45 + 2.651 + 2.16 = 12.26 ct/kWh ≈ 0.00012 €/Wh
RETAIL_MARKUP_EUR_PER_WH = 0.00012  # 12 ct/kWh

# Paths
RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"


def load_smard_csv(filepath: Path) -> pd.DataFrame:
    """Load SMARD CSV export with German formatting."""
    # Read as strings first to handle German number format
    df = pd.read_csv(filepath, sep=';', encoding='utf-8', dtype=str)
    
    # Keep only timestamp and DE/LU price columns
    time_col = 'Datum von'
    price_col = None
    
    for col in df.columns:
        if 'Deutschland' in col and '€/MWh' in col and 'Anrainer' not in col:
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Could not find DE/LU price column in {filepath}")
    
    df = df[[time_col, price_col]].copy()
    df.columns = ['time_raw', 'price_mwh']
    
    # Parse German datetime format
    df['time'] = pd.to_datetime(df['time_raw'], format='%d.%m.%Y %H:%M')
    
    # Convert German number format: replace comma with dot, handle '-' as NaN
    df['price_mwh'] = df['price_mwh'].str.replace(',', '.', regex=False)
    df['price_mwh'] = pd.to_numeric(df['price_mwh'], errors='coerce')
    df = df.dropna(subset=['price_mwh'])
    
    return df[['time', 'price_mwh']]


def transform_to_revoletion(
    df: pd.DataFrame,
    scale_factor: float = 1.0,
    retail_markup: float = RETAIL_MARKUP_EUR_PER_WH
) -> pd.DataFrame:
    """
    Convert SMARD prices to REVOL-E-TION format.
    
    Args:
        df: DataFrame with columns [time, price_mwh]
        scale_factor: Multiplier for future price scenarios (e.g., 0.95 for -5%)
        retail_markup: Additional cost on top of wholesale price (€/Wh)
    
    Returns:
        DataFrame with columns [time, cost] ready for REVOL-E-TION
    """
    result = pd.DataFrame()
    
    # Format timestamp with timezone (CET/CEST)
    result['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S+01:00')
    
    # Convert €/MWh → €/Wh and add retail markup
    wholesale_eur_per_wh = df['price_mwh'] / 1_000_000
    
    # Apply scaling factor (for future scenarios)
    wholesale_scaled = wholesale_eur_per_wh * scale_factor
    
    # Add retail markup (network fees, taxes, etc.)
    result['cost'] = wholesale_scaled + retail_markup
    
    return result


def process_file(
    input_path: Path,
    output_path: Path,
    scale_factor: float = 1.0
) -> None:
    """Process a single SMARD file."""
    print(f"Loading: {input_path.name}")
    df = load_smard_csv(input_path)
    
    print(f"  Records: {len(df)}")
    print(f"  Date range: {df['time'].min()} to {df['time'].max()}")
    print(f"  Price range: {df['price_mwh'].min():.2f} to {df['price_mwh'].max():.2f} €/MWh")
    print(f"  Negative hours: {(df['price_mwh'] < 0).sum()}")
    
    result = transform_to_revoletion(df, scale_factor=scale_factor)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    print(f"  Saved: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Transform SMARD data to REVOL-E-TION format")
    parser.add_argument('--year', type=int, help="Process specific year only")
    parser.add_argument('--scale', type=float, default=1.0, help="Price scaling factor")
    parser.add_argument('--input', type=Path, help="Specific input file")
    args = parser.parse_args()
    
    if args.input:
        input_path = args.input
        year = args.year or input_path.stem.split('_')[-1][:4]
        output_path = PROCESSED_DIR / f"grid_opex_g2s_{year}.csv"
        process_file(input_path, output_path, scale_factor=args.scale)
    else:
        raw_files = list(RAW_DIR.glob("*.csv"))
        if not raw_files:
            print(f"No CSV files found in {RAW_DIR}")
            return
        
        for input_path in sorted(raw_files):
            year = args.year or '2025'
            for part in input_path.stem.split('_'):
                if part.isdigit() and len(part) == 4:
                    year = part
                    break
            
            output_path = PROCESSED_DIR / f"grid_opex_g2s_{year}.csv"
            process_file(input_path, output_path, scale_factor=args.scale)


if __name__ == "__main__":
    main()
