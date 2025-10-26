import pandas as pd

def load_and_clean_data(config):
    """
    Loads and cleans respondent data based on a configuration dictionary.
    Includes detailed printouts of students removed at each step.
    
    Args:
        config (dict): A dictionary containing 'file_path', 'complete_action',
                       and 'filter_pauses'.
    """
    try:
        file_path = config['file_path']
        df = pd.read_csv(file_path)

        # --- Initial Count ---
        initial_count = df['Assignment'].nunique()
        print("\n--- Data Cleaning Funnel ---")
        print(f"Step 1: Initial total unique students loaded: {initial_count}")

        # --- Data Cleaning ---
        df['Action'] = df['Action'].astype(str)
        
        # --- Pause Filter ---
        if config.get('filter_pauses', True):
            pause_actions = df[df['Action'].str.contains('pause', case=False, na=False)]
            assignments_with_pause = pause_actions["Assignment"].unique()
            
            print(f"Step 2: Removing {len(assignments_with_pause)} students with 'pause' actions...")
            df = df[~df["Assignment"].isin(assignments_with_pause)]
            
            count_after_pause_filter = df['Assignment'].nunique()
            print(f"       Remaining students: {count_after_pause_filter}")
        else:
            print("Step 2: Skipping 'pause' filter (as configured)...")
            count_after_pause_filter = initial_count # No change

        # --- Completion Filter ---
        count_before_completion_filter = df['Assignment'].nunique()
        
        complete_action = config['complete_action']
        completed_actions = df[df['Action'] == complete_action]
        completed_assignments_ids = completed_actions['Assignment'].unique()
        
        df = df[df['Assignment'].isin(completed_assignments_ids)]
        
        count_after_completion_filter = df['Assignment'].nunique()
        removed_count = count_before_completion_filter - count_after_completion_filter
        
        print(f"Step 3: Removing {removed_count} students who did not complete the assessment...")
        print(f"       Remaining students: {count_after_completion_filter}")

        # --- Time Calculations ---
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
        df.dropna(subset=['datetime'], inplace=True)

        time_per_respondent = df.groupby('Assignment')['datetime'].agg(['min', 'max'])
        time_per_respondent['duration'] = time_per_respondent['max'] - time_per_respondent['min']
        
        count_before_time_filter = len(time_per_respondent)
        
        # --- Time Filter ---
        time_limit_max = pd.Timedelta(minutes = 600)
        time_limit_min = pd.Timedelta(minutes=1)
        time_filtered_df = time_per_respondent[(time_per_respondent['duration'] < time_limit_max) & (time_per_respondent["duration"] > time_limit_min)]
        time_filtered_df.reset_index(inplace=True)
        
        count_after_time_filter = len(time_filtered_df)
        removed_count = count_before_time_filter - count_after_time_filter
        
        print(f"Step 4: Removing {removed_count} students with durations < 1 min or > 10 hrs...")
        print(f"       Final analytic sample: {count_after_time_filter} students")
        print("---------------------------------")

        print(f"\nData loading and cleaning complete for: {file_path}")
        return df, time_filtered_df

    except FileNotFoundError:
        print(f"Error: The file '{config['file_path']}' was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return None, None