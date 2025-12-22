#!/usr/bin/env python3
"""
Transform netztransparenz.de Monatsmarktwerte to REVOL-E-TION grid opex S2G format.

Input:  Monatsmarktwerte CSV from netztransparenz.de (monthly solar market values)
Output: grid_opex_s2g_YYYY.csv with columns [time, cost] in €/Wh (negative = revenue)

Usage:
    python transform.py                          # Process raw file
    python transform.py --year 2025              # Specify year
    python transform.py --scale 0.95             # Apply price scaling for future stages
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Paths
RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"


def load_monatsmarktwerte(filepath: Path) -> dict:
    """
    Load netztransparenz.de Monatsmarktwerte CSV.
    Returns dict with month -> value in ct/kWh
    """
    df = pd.read_csv(filepath, sep=';', encoding='utf-8', dtype=str)
    
    # Find MW Solar row
    solar_row = None
    for idx, row in df.iterrows():
        if 'MW Solar' in str(row.iloc[0]):
            solar_row = row
            break
    
    if solar_row is None:
        raise ValueError("Could not find 'MW Solar' row in file")
    
    # Extract monthly values
    months = {}
    month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    
    for i, col in enumerate(df.columns[1:13]):  # Skip first column (label)
        value_str = solar_row.iloc[i + 1]
        if pd.notna(value_str) and value_str.strip():
            # Handle German decimal format
            value = float(value_str.strip().replace(',', '.'))
            months[i + 1] = value  # month number -> ct/kWh
    
    return months


def expand_to_hourly(monthly_values: dict, year: int) -> pd.DataFrame:
    """
    Expand monthly values to hourly timeseries for the full year.
    """
    # Create hourly datetime index for the year
    start = pd.Timestamp(f'{year}-01-01 00:00:00', tz='Europe/Berlin')
    end = pd.Timestamp(f'{year}-12-31 23:00:00', tz='Europe/Berlin')
    dti = pd.date_range(start=start, end=end, freq='H')
    
    # Assign monthly value to each hour
    values = []
    for dt in dti:
        month = dt.month
        if month in monthly_values:
            values.append(monthly_values[month])
        else:
            # Use average of available months if month missing
            values.append(np.mean(list(monthly_values.values())))
    
    return pd.DataFrame({'time': dti, 'value_ct_kwh': values})


def transform_to_revoletion(
    df: pd.DataFrame,
    scale_factor: float = 1.0
) -> pd.DataFrame:
    """
    Convert to REVOL-E-TION format.
    
    - Convert ct/kWh to €/Wh
    - Make negative (revenue for site)
    - Apply scaling factor
    """
    result = pd.DataFrame()
    
    # Format timestamp
    result['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S+01:00')
    
    # Convert ct/kWh to €/Wh: divide by 100 (ct->€) and by 1000 (kWh->Wh)
    # = divide by 100,000
    # Make negative because this is revenue (site sells to grid)
    result['cost'] = -(df['value_ct_kwh'] * scale_factor / 100000)
    
    return result


def process_file(
    input_path: Path,
    output_path: Path,
    year: int,
    scale_factor: float = 1.0
) -> None:
    """Process monatsmarktwerte file."""
    print(f"Loading: {input_path.name}")
    monthly_values = load_monatsmarktwerte(input_path)
    
    print(f"  Months with data: {len(monthly_values)}")
    print(f"  Values (ct/kWh): {list(monthly_values.values())}")
    print(f"  Average: {np.mean(list(monthly_values.values())):.2f} ct/kWh")
    
    df = expand_to_hourly(monthly_values, year)
    result = transform_to_revoletion(df, scale_factor=scale_factor)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    print(f"  Saved: {output_path.name}")
    print(f"  Records: {len(result)}")


def main():
    parser = argparse.ArgumentParser(description="Transform Monatsmarktwerte to REVOL-E-TION format")
    parser.add_argument('--year', type=int, default=2025, help="Year for output file")
    parser.add_argument('--scale', type=float, default=1.0, help="Price scaling factor")
    parser.add_argument('--input', type=Path, help="Specific input file")
    args = parser.parse_args()
    
    if args.input:
        input_path = args.input
    else:
        # Find first CSV in raw directory
        raw_files = list(RAW_DIR.glob("*.csv"))
        if not raw_files:
            print(f"No CSV files found in {RAW_DIR}")
            return
        input_path = raw_files[0]
    
    output_path = PROCESSED_DIR / f"grid_opex_s2g_{args.year}.csv"
    process_file(input_path, output_path, args.year, scale_factor=args.scale)


if __name__ == "__main__":
    main()
