#!/usr/bin/env python3
"""
Timeframe mapper for Schmid depot BEV fleet.
Maps simulation timesteps to demand profiles.
"""

def map_timeframes(df, name, scenario):
    cs_map = {'bev': map_timeframes_bev}
    return cs_map[name](df, scenario)


def map_timeframes_bev(df, scenario):
    """
    Map timeframes for BEV fleet.
    Currently uses single timeframe 'A' for all periods.
    """
    condition = df.index.weekday > 4  # Weekend

    df.loc[condition, 'timeframe'] = 'A'
    df.loc[condition, 'demand_mean'] = 5
    df.loc[condition, 'demand_std'] = 2

    df.loc[~condition, 'timeframe'] = 'A'
    df.loc[~condition, 'demand_mean'] = 5
    df.loc[~condition, 'demand_std'] = 2

    return df['timeframe'], df['demand_mean'], df['demand_std']
