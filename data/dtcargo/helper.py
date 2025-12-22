import pandas as pd
import ast

def initialize_empty_log(parameters, scenario):
    """ 
    initializes an empty log dataframe that is supposed to be filled and converted to CSV later on
    """

    # Retrieve values from DataFrame
    starttime_str = parameters.loc[("scenario", "starttime"), scenario]
    timestep_str = parameters.loc[("scenario", "timestep"), scenario]
    sim_duration_str = parameters.loc[("scenario", "sim_duration"), scenario]

    # Type conversion to Datetime objects
    starttime = pd.to_datetime(starttime_str, dayfirst=True) 
    timestep = pd.to_timedelta(timestep_str)                     
    sim_duration = int(sim_duration_str)                         

    # Calculate endtime
    endtime = starttime + pd.Timedelta(days=sim_duration)

    # Create timeline for indices – exclude endtime so that exactly sim_duration days are created
    time_index = pd.date_range(start=starttime,
                                end=endtime,
                                freq=timestep,
                                inclusive="left"
                                )
    
    # Create MultiIndex for columns
    num_vehicles = parameters.loc[("bev", "num"), scenario]
    vehicles = [f"bev{v}" for v in range(1,num_vehicles+1)]

    attributes = ["atbase", "dsoc", "consumption", "atac", "atdc", "dist"]
    bool_attrs = ["atbase", "atac", "atdc"] 

    tuples = [(veh, attr) for veh in vehicles for attr in attributes]
    columns = pd.MultiIndex.from_tuples(tuples)
    
    # Initialize Dataframe with respective indeices and colmuns
    log = pd.DataFrame(0.0, index=time_index, columns=columns)

    # Set boolean columns
    for attr in bool_attrs:
        for veh in vehicles:
            log[(veh, attr)] = False

    log.index = log.index.tz_localize("UTC").tz_convert("Europe/Berlin")
    
    return log


def load_tracks(path_tracks_with_energy):
    """ 
    reads the input data from tracks_with_energy.csv and stores it in a dataframe 
    """

    # Read input data
    df=pd.read_csv(path_tracks_with_energy)

    # Save time data in the correct format
    df["start_time"] = pd.to_datetime(df["start_time"], format="mixed", utc=True).dt.tz_convert("Europe/Berlin")
    df["stop_time"]  = pd.to_datetime(df["stop_time"], format="mixed", utc=True).dt.tz_convert("Europe/Berlin")

    return df


def load_scenarios(path_scenario_data):
    """ 
    reads the input data from scenarios_example.csv and stores it in a dataframe 
    """

    # Read input data
    parameters = pd.read_csv(path_scenario_data,
                            index_col=[0, 1],
                            keep_default_na=False)

    return parameters.sort_index(sort_remaining=True).map(infer_dtype)


def infer_dtype(value):
    """
    infer the data type of a value from a string representation. To be used as a .map(infer_dtype) function.
    """

    # remove whitespace at beginning or end of string (convert to string, as nan already is of type float)
    value = str(value).strip()

    try:
        return int(value)
    except (ValueError or OverflowError):
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    elif value.lower() in ['none', 'null', 'nan', '']:
        return None

    try:
        evaluated = ast.literal_eval(value)
        if isinstance(evaluated, dict):
            return evaluated
        elif isinstance(evaluated, list):
            return evaluated
    except (ValueError, SyntaxError):
        pass

    return value.lower()


def sample_tracks_in_log(tracks_with_energy, log, parameters, scenario):
    """ 
    retrieves the trip data from tracks_with_energy and writes it to the time series of the log file 
    """

    # Store the respective column containing the consumption in kwh/km
    avg_spec_consumption = tracks_with_energy["avg_energy_consumption_kwh/km_cleaned"].mean()

    # Store the number of vehicles and simulation starttime indicated for the respective scenario
    num_vehicles = int(parameters.loc[("bev", "num"), scenario])
    timestep = parameters.loc[("scenario", "timestep"), scenario]

    # Iterate over the individual vehicles and store the vehicle's tracks
    for vehicle_id in range(1, num_vehicles+1):
        vehicle_tracks = tracks_with_energy[tracks_with_energy["vehicle_id"] == vehicle_id].sort_values("start_time")

        # Iterate over the respective vehicle's tracks
        for _, row in vehicle_tracks.iterrows():
            # Store respective track data
            start, end = row["start_time"], row["stop_time"]
            dist = row["distance_km"]
            energy_consumption_kwh = row["energy_consumption_kwh"]

            # Calculate the track duration in minutes
            duration_minutes = (end - start).total_seconds() / 60

            # Mask all timesteps in log within the track
            mask = (log.index >= start.floor(timestep)) & (log.index < end.ceil(timestep))
            bins = log.index[mask]

            # Set the trip distance which is indicated only in the first timestep
            if len(bins) > 0:
                log.loc[bins[0], (f"bev{vehicle_id}", "dist")] = dist 

            # Iterate over the masked timesteps
            for t in bins:
                interval_start = t
                interval_end = t + pd.Timedelta(timestep)
                overlap = (min(end, interval_end) - max(start, interval_start)).total_seconds() / 60.0
                if overlap <= 0:
                    continue

                share = overlap / duration_minutes
                # Fill empty fields with average values and fill the remaining fields with recorded values (as 
                # some entries in tracks_with_energy are empty)
                if pd.isna(energy_consumption_kwh) or energy_consumption_kwh == "":
                    consumption = avg_spec_consumption * dist * share
                else:
                    consumption = energy_consumption_kwh * share

                # Store results in log
                log.loc[t, (f"bev{vehicle_id}", "consumption")] = consumption * 1000 / 0.25 # Convert kWh to W

            # Set atbase for the successive timesteps if the trip ends at the homebase
            if row["home_base"]:
                # Get the next track entry 
                next_trips = vehicle_tracks[vehicle_tracks["start_time"] > end]

                # Check if a next track exists, otherwise take the last time step from the log file
                next_start = next_trips.iloc[0]["start_time"] if not next_trips.empty else log.index.max()

                # Set all 15-minute slots between stop_time and next start_time
                mask_atbase = (log.index >= end.ceil(timestep)) & (log.index < next_start)
                log.loc[mask_atbase, (f"bev{vehicle_id}", "atbase")] = True
    
    return log


def set_constant_columns(log, parameters):
    """ 
    sets the boolean columns atac and atdc permanently True for all vehicles
    """

    # Iterate over the atac and atdc columns in the log file
    for v in range(1,parameters.loc[("bev", "num"), "bev_grid"]+1):
        log.loc[:, (f"bev{v}", ["atac", "atdc"])] = True

    return log

def save_log(scenario, filled_log):
    """ 
    converts the filled dataframe to CSV
    """
    filled_log.to_csv("output/log_" + scenario + ".csv")