"""
Fleet Scaler for multi-stage optimization.

Scales bev_log files by cloning existing vehicle columns to simulate fleet growth.
Uses random selection to pick which vehicles to clone.

Author: STRIDE
"""

import random
from pathlib import Path
from typing import Optional

import pandas as pd


def scale_bev_log(
    base_log_path: Path,
    output_path: Path,
    base_vehicles: int,
    target_vehicles: int,
    seed: Optional[int] = 42
) -> Path:
    """
    Scale bev_log by cloning existing vehicle columns.
    
    For target=100, base=84:
    - Keep all 84 original vehicles (bev0-bev83)
    - Add 16 cloned vehicles (bev84-bev99 = random copies of existing)
    
    Parameters
    ----------
    base_log_path : Path
        Path to original bev_log CSV file
    output_path : Path
        Path for output scaled bev_log file
    base_vehicles : int
        Number of vehicles in base log (e.g., 84)
    target_vehicles : int
        Target number of vehicles (e.g., 100)
    seed : int, optional
        Random seed for reproducibility (default: 42)
        
    Returns
    -------
    Path
        Path to created scaled bev_log file
    """
    if target_vehicles <= base_vehicles:
        # No scaling needed - just copy the file
        if output_path != base_log_path:
            import shutil
            shutil.copy(base_log_path, output_path)
        return output_path
    
    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)
    
    # Read the base log
    df = pd.read_csv(base_log_path, header=[0, 1])
    
    # Get column structure: first level is vehicle ID, second level is attribute
    # Format: (bevX, atbase), (bevX, dsoc), (bevX, consumption), etc.
    
    # Identify existing vehicle IDs (excluding 'time' column)
    existing_vehicles = sorted(set(
        col[0] for col in df.columns if col[0] != 'time' and col[0].startswith('bev')
    ), key=lambda x: int(x[3:]))  # Sort by numeric part
    
    if len(existing_vehicles) != base_vehicles:
        raise ValueError(
            f"Expected {base_vehicles} vehicles in base log, "
            f"found {len(existing_vehicles)}: {existing_vehicles[:5]}..."
        )
    
    # Calculate how many new vehicles to add
    vehicles_to_add = target_vehicles - base_vehicles
    
    # Randomly select which existing vehicles to clone
    vehicles_to_clone = random.choices(existing_vehicles, k=vehicles_to_add)
    
    # Create new columns for cloned vehicles
    new_columns_data = {}
    for i, source_vehicle in enumerate(vehicles_to_clone):
        new_vehicle_id = f"bev{base_vehicles + i}"
        
        # Get all columns for the source vehicle
        source_cols = [col for col in df.columns if col[0] == source_vehicle]
        
        for source_col in source_cols:
            # Create new column with same data, new vehicle ID
            new_col_name = (new_vehicle_id, source_col[1])
            new_columns_data[new_col_name] = df[source_col].values
    
    # Add all new columns at once using pd.concat (avoids fragmentation)
    if new_columns_data:
        new_df = pd.DataFrame(new_columns_data, index=df.index)
        df = pd.concat([df, new_df], axis=1)
    
    # Sort columns: time first, then vehicles in numeric order
    def col_sort_key(col):
        if col[0] == 'time':
            return (-1, '')  # time comes first
        vehicle_num = int(col[0][3:])  # extract number from 'bevX'
        attr_order = ['atbase', 'dsoc', 'consumption', 'atac', 'atdc', 'tour_dist']
        attr_idx = attr_order.index(col[1]) if col[1] in attr_order else 99
        return (vehicle_num, attr_idx)
    
    sorted_columns = sorted(df.columns.tolist(), key=col_sort_key)
    df = df[sorted_columns]
    
    # Save to output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"    • Scaled bev_log: {base_vehicles} → {target_vehicles} vehicles")
    print(f"    • Cloned vehicles: {vehicles_to_clone[:5]}{'...' if len(vehicles_to_clone) > 5 else ''}")
    
    return output_path


def get_vehicle_count(bev_log_path: Path) -> int:
    """
    Count the number of vehicles in a bev_log file.
    
    Parameters
    ----------
    bev_log_path : Path
        Path to bev_log CSV file
        
    Returns
    -------
    int
        Number of unique vehicles
    """
    # Read just the header
    df = pd.read_csv(bev_log_path, header=[0, 1], nrows=0)
    
    # Count unique vehicle IDs
    vehicles = set(
        col[0] for col in df.columns if col[0] != 'time' and col[0].startswith('bev')
    )
    
    return len(vehicles)
