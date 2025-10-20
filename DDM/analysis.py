import pandas as pd

def load_and_clean_data(config):
    """
    Loads and cleans respondent data based on a configuration dictionary.
    
    Args:
        config (dict): A dictionary containing 'file_path' and 'complete_action'.
    """
    try:
        # Get the file path from the configuration
        file_path = config['file_path']
        df = pd.read_csv(file_path)

        # --- Data Cleaning ---
        df['Action'] = df['Action'].astype(str)
        pause_actions = df[df['Action'].str.contains('pause', case=False, na=False)]
        assignments_with_pause = pause_actions["Assignment"].unique()
        df = df[~df["Assignment"].isin(assignments_with_pause)]

        # Get the unique completion action from the configuration
        complete_action = config['complete_action']
        
        completed_actions = df[df['Action'] == complete_action]
        completed_assignments_ids = completed_actions['Assignment'].unique()
        df = df[df['Assignment'].isin(completed_assignments_ids)]

        # --- Time Calculations ---
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        df.dropna(subset=['datetime'], inplace=True)

        time_per_respondent = df.groupby('Assignment')['datetime'].agg(['min', 'max'])
        time_per_respondent['duration'] = time_per_respondent['max'] - time_per_respondent['min']

        time_limit_max = pd.Timedelta(hours=10)
        time_limit_min = pd.Timedelta(minutes=1)
        time_filtered_df = time_per_respondent[(time_per_respondent['duration'] < time_limit_max) & (time_per_respondent["duration"] > time_limit_min)]
        time_filtered_df.reset_index(inplace=True)

        print(f"Data loading and cleaning complete for: {file_path}")
        return df, time_filtered_df

    except FileNotFoundError:
        print(f"Error: The file '{config['file_path']}' was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return None, None