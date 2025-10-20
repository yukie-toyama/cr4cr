import pandas as pd

def load_and_clean_data(file_path):
    """
    Loads the respondent data, cleans it by removing pauses, incomplete
    sessions, and time outliers, and returns the processed DataFrames.
    """
    try:
        df = pd.read_csv(file_path)

        # --- Data Cleaning ---
        df['Action'] = df['Action'].astype(str)
        pause_actions = df[df['Action'].str.contains('pause', case=False, na=False)]
        assignments_with_pause = pause_actions["Assignment"].unique()
        df = df[~df["Assignment"].isin(assignments_with_pause)]

        complete_action = "End activity Spring 2025 MS DDM Administration"
        completed_actions = df[df['Action'] == complete_action]
        completed_assignments_ids = completed_actions['Assignment'].unique()
        df = df[df['Assignment'].isin(completed_assignments_ids)]

        # --- Time Calculations ---
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        df.dropna(subset=['datetime'], inplace=True)

        time_per_respondent = df.groupby('Assignment')['datetime'].agg(['min', 'max'])
        time_per_respondent['duration'] = time_per_respondent['max'] - time_per_respondent['min']

        time_limit_max = pd.Timedelta(hours=24)
        time_limit_min = pd.Timedelta(minutes=1)
        time_filtered_df = time_per_respondent[(time_per_respondent['duration'] < time_limit_max) & (time_per_respondent["duration"] > time_limit_min)]
        time_filtered_df.reset_index(inplace=True)

        print("Data loading and cleaning complete.")
        # Return both the main df and the time-filtered summary
        return df, time_filtered_df

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return None, None