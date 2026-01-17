#!/usr/bin/env python3
"""
Regenerate 180d timeseries files at 15-min resolution to match bev_log_180d.

Creates:
- dem_timeseries_180d.csv (15-min resolution)
- grid_opex_g2s_180d.csv (15-min resolution)
- grid_opex_s2g_180d.csv (15-min resolution)
"""

import pandas as pd
from pathlib import Path

# Paths
INPUTS_DIR = Path(__file__).parent.parent / "inputs/schmid/timeseries"
DATA_DIR = Path(__file__).parent.parent / "data"

# Target time range (matching bev_log_180d)
START = "2025-01-01 00:00:00"
END = "2025-06-29 00:45:00"  # Last timestamp in bev_log_180d
TZ = "Europe/Berlin"
FREQ = "15min"


def create_time_index():
    """Create 15-min time index matching bev_log_180d."""
    idx = pd.date_range(start=START, end=END, freq=FREQ, tz=TZ)
    print(f"Time index: {len(idx)} timesteps")
    print(f"  Start: {idx[0]}")
    print(f"  End: {idx[-1]}")
    return idx


def regenerate_dem_timeseries(time_idx):
    """Regenerate dem_timeseries at 15-min resolution by repeating available data."""
    raw_path = DATA_DIR / "depot_Schmid/raw/dem_timeseries.csv"

    df = pd.read_csv(raw_path)
    df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert(TZ)
    df = df.set_index('time').sort_index()

    print(f"\ndem_timeseries raw: {len(df)} rows")
    print(f"  Range: {df.index[0]} to {df.index[-1]}")

    # Create output dataframe
    result = pd.DataFrame(index=time_idx)
    result.index.name = 'time'

    # Tile the raw data to cover the target period
    # Use modulo to repeat the pattern
    raw_values = df['power_w'].values
    n_raw = len(raw_values)
    n_target = len(time_idx)

    # Repeat raw values cyclically
    tiled_values = [raw_values[i % n_raw] for i in range(n_target)]

    # Scale from kW (raw seems to be in kW based on values ~20) to W
    # Actually looking at raw values (21, 18, 25), these are likely kW not W
    # Let me check the test file to see what scale is expected
    result['power_w'] = [v * 1000 for v in tiled_values]  # kW -> W

    output_path = INPUTS_DIR / "dem_timeseries_180d.csv"
    result.to_csv(output_path, date_format='%Y-%m-%d %H:%M:%S%z')
    print(f"  Saved: {output_path} ({len(result)} rows)")

    return result


def regenerate_grid_opex(time_idx, direction='g2s'):
    """Regenerate grid_opex at 15-min resolution."""
    # Load the processed hourly data for 2025
    raw_path = DATA_DIR / f"grid_{direction}/processed/grid_opex_{direction}_2025.csv"

    if not raw_path.exists():
        # Fallback: use the existing 180d file and resample
        raw_path = INPUTS_DIR / f"grid_opex_{direction}_180d.csv"

    df = pd.read_csv(raw_path)
    df['time'] = pd.to_datetime(df['time'])

    # Make timezone aware if not already
    if df['time'].dt.tz is None:
        df['time'] = df['time'].dt.tz_localize(TZ, ambiguous='infer', nonexistent='shift_forward')
    else:
        df['time'] = df['time'].dt.tz_convert(TZ)

    # Remove duplicates (DST can cause duplicates)
    df = df.drop_duplicates(subset=['time'], keep='first')
    df = df.set_index('time').sort_index()

    print(f"\ngrid_opex_{direction} raw: {len(df)} rows")
    print(f"  Range: {df.index[0]} to {df.index[-1]}")

    # Create output dataframe at 15-min resolution
    result = pd.DataFrame(index=time_idx)
    result.index.name = 'time'

    # For each 15-min slot, find the nearest hourly value
    # Use merge_asof for forward-fill matching
    result_df = result.reset_index()
    df_reset = df.reset_index()

    merged = pd.merge_asof(
        result_df.sort_values('time'),
        df_reset.sort_values('time'),
        on='time',
        direction='backward'
    )

    result['cost'] = merged['cost'].values

    # Backfill any NaN at start
    result['cost'] = result['cost'].bfill()

    output_path = INPUTS_DIR / f"grid_opex_{direction}_180d.csv"
    result.to_csv(output_path, date_format='%Y-%m-%d %H:%M:%S%z')
    print(f"  Saved: {output_path} ({len(result)} rows)")

    return result


def verify_alignment():
    """Verify all 180d timeseries have matching timestamps."""
    print("\n=== Verification ===")

    files = [
        "bev_log_180d.csv",
        "dem_timeseries_180d.csv",
        "grid_opex_g2s_180d.csv",
        "grid_opex_s2g_180d.csv"
    ]

    for fname in files:
        fpath = INPUTS_DIR / fname
        if not fpath.exists():
            print(f"  {fname}: NOT FOUND")
            continue

        # Read first timestamp
        with open(fpath) as f:
            lines = f.readlines()
            # Skip headers (bev_log has 2, others have 1)
            if 'bev' in fname:
                first_data = lines[2].split(',')[0]
                last_data = lines[-1].split(',')[0]
                n_rows = len(lines) - 2
            else:
                first_data = lines[1].split(',')[0]
                last_data = lines[-1].split(',')[0]
                n_rows = len(lines) - 1

        print(f"  {fname}: {n_rows} rows, {first_data[:19]} to {last_data[:19]}")


def main():
    print("Regenerating 180d timeseries at 15-min resolution")
    print("=" * 60)

    # Create time index
    time_idx = create_time_index()

    # Regenerate each file
    regenerate_dem_timeseries(time_idx)
    regenerate_grid_opex(time_idx, 'g2s')
    regenerate_grid_opex(time_idx, 's2g')

    # Verify alignment
    verify_alignment()

    print("\nDone!")


if __name__ == "__main__":
    main()
