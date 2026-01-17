#!/usr/bin/env python3
"""
Transform DT-Cargo tracks_with_energy.csv to REVOL-E-TION bev_log.csv for Depot Schmid.

Filters by freight_forwarder=6 (Schmid) and generates 15-min interval BEV usage log.

Usage:
    python transform.py
    python transform.py --start 2021-09-01 --days 365
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Configuration
FREIGHT_FORWARDER_ID = 6
DEPOT_NAME = "Schmid"

# Paths
RAW_DIR = Path(__file__).parent.parent / "dtcargo" / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"

# Default simulation parameters
DEFAULT_START = "2023-06-02"  # First date in Schmid's DT-Cargo data
DEFAULT_DAYS = 249  # Data covers ~249 days (Jun 2023 - Feb 2024)
DEFAULT_TIMESTEP = "15min"


def load_tracks(filepath: Path, freight_forwarder: int) -> pd.DataFrame:
    """Load and filter tracks_with_energy.csv by freight_forwarder."""
    df = pd.read_csv(filepath)

    # Filter by freight forwarder
    df = df[df["freight_forwarder"] == freight_forwarder].copy()

    # Parse timestamps
    df["start_time"] = pd.to_datetime(df["start_time"], format="mixed", utc=True).dt.tz_convert("Europe/Berlin")
    df["stop_time"] = pd.to_datetime(df["stop_time"], format="mixed", utc=True).dt.tz_convert("Europe/Berlin")

    return df


def get_vehicle_ids(tracks: pd.DataFrame) -> list:
    """Get sorted list of unique vehicle IDs."""
    return sorted(tracks["vehicle_id"].unique())


def initialize_empty_log(starttime: pd.Timestamp, days: int, timestep: str, vehicle_ids: list) -> pd.DataFrame:
    """Create empty log DataFrame with proper structure."""
    endtime = starttime + pd.Timedelta(days=days)

    time_index = pd.date_range(
        start=starttime,
        end=endtime,
        freq=timestep,
        inclusive="left"
    )

    # Create vehicle labels (bev0, bev1, ...)
    vehicles = [f"bev{i}" for i in range(len(vehicle_ids))]
    attributes = ["atbase", "dsoc", "consumption", "atac", "atdc", "tour_dist"]

    tuples = [(veh, attr) for veh in vehicles for attr in attributes]
    columns = pd.MultiIndex.from_tuples(tuples)

    log = pd.DataFrame(0.0, index=time_index, columns=columns)

    # Initialize boolean columns
    # atbase=True at start (assume all vehicles at depot at simulation start)
    # atac/atdc=False (will be set to True later)
    for veh in vehicles:
        log[(veh, "atbase")] = True  # Start at depot
        log[(veh, "atac")] = False
        log[(veh, "atdc")] = False

    return log


def sample_tracks_in_log(tracks: pd.DataFrame, log: pd.DataFrame, vehicle_ids: list, timestep: str) -> pd.DataFrame:
    """Map track data to 15-min bins in log."""

    # Calculate average consumption for fallback
    avg_spec_consumption = tracks["avg_energy_consumption_kwh/km_cleaned"].mean()

    # Create mapping from actual vehicle_id to bev index
    vid_to_bev = {vid: f"bev{i}" for i, vid in enumerate(vehicle_ids)}

    for vehicle_id in vehicle_ids:
        bev_label = vid_to_bev[vehicle_id]
        vehicle_tracks = tracks[tracks["vehicle_id"] == vehicle_id].sort_values("start_time")

        for _, row in vehicle_tracks.iterrows():
            start, end = row["start_time"], row["stop_time"]
            dist_km = row["distance_km"]
            energy_kwh = row["energy_consumption_kwh"]

            # Skip if outside simulation window
            if end < log.index.min() or start > log.index.max():
                continue

            duration_minutes = (end - start).total_seconds() / 60
            if duration_minutes <= 0:
                continue

            # Find bins that overlap with this track
            mask = (log.index >= start.floor(timestep)) & (log.index < end.ceil(timestep))
            bins = log.index[mask]

            if len(bins) == 0:
                continue

            # Set tour distance in first bin (in meters)
            log.loc[bins[0], (bev_label, "tour_dist")] += dist_km * 1000

            # Distribute consumption across bins
            for t in bins:
                interval_start = t
                interval_end = t + pd.Timedelta(timestep)

                # Calculate overlap
                overlap_start = max(start, interval_start)
                overlap_end = min(end, interval_end)
                overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60

                if overlap_minutes <= 0:
                    continue

                share = overlap_minutes / duration_minutes

                # Calculate consumption for this interval
                if pd.isna(energy_kwh) or energy_kwh == "":
                    consumption_kwh = avg_spec_consumption * dist_km * share
                else:
                    consumption_kwh = energy_kwh * share

                # Convert kWh to W (power over 15-min interval)
                # kWh / 0.25h = kW, then * 1000 = W
                consumption_w = consumption_kwh * 1000 / 0.25

                log.loc[t, (bev_label, "consumption")] += consumption_w

                # Vehicle is NOT at base while driving
                log.loc[t, (bev_label, "atbase")] = False

            # Set atbase=True for time between this trip ending at home and next trip
            if row["home_base"]:
                next_trips = vehicle_tracks[vehicle_tracks["start_time"] > end]
                next_start = next_trips.iloc[0]["start_time"] if not next_trips.empty else log.index.max()

                mask_atbase = (log.index >= end.ceil(timestep)) & (log.index < next_start)
                log.loc[mask_atbase, (bev_label, "atbase")] = True

                # Set dsoc=1 at the timestep when vehicle returns (signals charging need)
                return_bin = end.ceil(timestep)
                if return_bin in log.index:
                    log.loc[return_bin, (bev_label, "dsoc")] = 1

    # Set atac=True when at base (vehicle can charge at depot AC charger)
    # atdc remains False (no DC fast charging at depot - only AC)
    for i in range(len(vehicle_ids)):
        bev = f"bev{i}"
        log.loc[:, (bev, "atac")] = log[(bev, "atbase")]  # Can charge when at base
        log.loc[:, (bev, "atdc")] = False

    return log


def format_for_revoletion(log: pd.DataFrame) -> pd.DataFrame:
    """Format log for REVOL-E-TION output (matching Franziska's format)."""
    # Reset index to make time a column
    output = log.copy()
    output.index.name = "time"
    output = output.reset_index()

    # Flatten multi-index columns
    output.columns = ["time"] + [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col
                                 for col in output.columns[1:]]

    return output


def save_revoletion_format(log: pd.DataFrame, output_path: Path):
    """Save in exact REVOL-E-TION bev_log format with multi-row header."""
    # Get vehicle names and attributes
    vehicles = sorted(set(col[0] for col in log.columns))
    attributes = ["atbase", "dsoc", "consumption", "atac", "atdc", "tour_dist"]

    with open(output_path, 'w') as f:
        # First header row: time, then vehicle names repeated
        header1 = ["time"] + [veh for veh in vehicles for _ in attributes]
        f.write(",".join(header1) + "\n")

        # Second header row: time, then attribute names repeated
        header2 = ["time"] + attributes * len(vehicles)
        f.write(",".join(header2) + "\n")

        # Data rows
        for timestamp, row in log.iterrows():
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S%z")
            # Insert colon in timezone offset
            time_str = time_str[:-2] + ":" + time_str[-2:]

            values = [time_str]
            for veh in vehicles:
                for attr in attributes:
                    val = row[(veh, attr)]
                    if attr in ["atbase", "atac", "atdc"]:
                        values.append(str(bool(val)))
                    elif attr == "dsoc":
                        values.append(str(int(val)))
                    else:
                        values.append(str(float(val)))

            f.write(",".join(values) + "\n")


def main():
    parser = argparse.ArgumentParser(description=f"Generate BEV log for {DEPOT_NAME}")
    parser.add_argument("--start", type=str, default=DEFAULT_START, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Simulation duration in days")
    parser.add_argument("--timestep", type=str, default=DEFAULT_TIMESTEP, help="Time resolution")
    args = parser.parse_args()

    # Find tracks file
    tracks_file = RAW_DIR / "tracks_with_energy.csv"
    if not tracks_file.exists():
        print(f"Error: {tracks_file} not found")
        return

    print(f"Processing depot: {DEPOT_NAME} (freight_forwarder={FREIGHT_FORWARDER_ID})")

    # Load and filter tracks
    tracks = load_tracks(tracks_file, FREIGHT_FORWARDER_ID)
    vehicle_ids = get_vehicle_ids(tracks)
    print(f"  Vehicles: {len(vehicle_ids)}")
    print(f"  Tracks: {len(tracks)}")

    # Initialize log
    starttime = pd.Timestamp(args.start, tz="Europe/Berlin")
    log = initialize_empty_log(starttime, args.days, args.timestep, vehicle_ids)
    print(f"  Time range: {log.index.min()} to {log.index.max()}")
    print(f"  Timesteps: {len(log)}")

    # Fill log with track data
    log = sample_tracks_in_log(tracks, log, vehicle_ids, args.timestep)

    # Save output
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "bev_log.csv"
    save_revoletion_format(log, output_path)
    print(f"  Saved: {output_path}")


if __name__ == "__main__":
    main()
