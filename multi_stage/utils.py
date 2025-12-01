"""Shared utilities for multi-stage optimization."""


def get_unit(block_name: str) -> str:
    """
    Get display unit for block type.

    Parameters
    ----------
    block_name : str
        Name of the block (e.g., 'pv1', 'ess1', 'ev_system')

    Returns
    -------
    str
        Display unit: 'kW' for PV, 'kWh' for ESS/battery, 'vehicles' for EV, 'W' otherwise
    """
    if 'pv' in block_name.lower():
        return 'kW'
    elif 'ess' in block_name.lower() or 'battery' in block_name.lower():
        return 'kWh'
    elif 'ev' in block_name.lower() or 'vehicle' in block_name.lower():
        return 'vehicles'
    else:
        return 'W'
