import pandas as pd

# Define the filename
file_path = 'Spring 2025 MS DDM Administration respondent actions.csv'

# Load the dataset from the CSV file
try:
    # Read the entire CSV into a DataFrame
    df = pd.read_csv(file_path)

    # Step 0
    print("\nStep 0: Clean the data by removing all users who paused and spent more than 1 day on assessment")

    print(df.columns)
    print("Number of respondents before cleaning")
    print(len(df.groupby("Assignment")))
    df['Action'] = df['Action'].astype(str)

    print("All action types")
    print(df["Action"].unique())

    pause_actions = df[df['Action'].str.contains('pause', case=False, na=False)]
    assignments_with_pause = pause_actions["Assignment"].unique()
    no_pause_df = df[~df["Assignment"].isin(assignments_with_pause)]
    df = no_pause_df
    print("Number of respondents after removing pauses")
    print(len(df.groupby("Assignment")))


    complete_action = "End activity Spring 2025 MS DDM Administration"

    completed_actions = df[df['Action'].str.contains(complete_action, case = False, na = False)]
    
    completed_assignments_ids = completed_actions['Assignment'].unique()

    df = df[df['Assignment'].isin(completed_assignments_ids)]
    print("Number of respondents after removing incomplete and paused assessments")
    print(len(df.groupby("Assignment")))

    #print(df["Activities"].unique())

    # Add this line after you load the CSV into 'df'
    #print(df['Action'].unique().tolist())

    # --- Step 1: Combine Date and Time into a single Datetime column ---
    # This is the most crucial step for time analysis.
    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
    
    # Drop rows where the datetime could not be parsed
    df.dropna(subset=['datetime'], inplace=True)

    print("--- Initial Data Inspection ---")
    print("Successfully loaded and processed the datetime column.")
    print(f"Total number of actions recorded: {len(df)}")

    # --- Step 2: Calculate Overall Time Span ---
    # Find the earliest and latest timestamps in the entire dataset.
    start_time = df['datetime'].min()
    end_time = df['datetime'].max()
    total_duration = end_time - start_time

    print("\n--- Overall Summary ---")
    print(f"Data ranges from: {start_time}")
    print(f"            to: {end_time}")
    print(f"Total duration of all activity: {total_duration}")

    # --- Step 3: Calculate Time Spent per Respondent ---
    # We group by 'Assignment' (each respondent) and find the time
    # between their first and last recorded action.
    time_per_respondent = df.groupby('Assignment')['datetime'].agg(['min', 'max'])
    time_per_respondent['duration'] = time_per_respondent['max'] - time_per_respondent['min']

    time_limit_max = pd.Timedelta(hours=10)
    time_limit_min = pd.Timedelta(minutes=1)
    time_per_respondent_under_24 = time_per_respondent[(time_per_respondent['duration'] < time_limit_max) & (time_per_respondent["duration"] > time_limit_min)]

    print("\n--- Time Spent per Respondent ---")
    print("Duration for the first 5 respondents:")
    print(time_per_respondent_under_24.head())
    print(f"\n The number of fully cleaned responses after removing time outliers is: {len(time_per_respondent_under_24)}")

    # --- Step 4: Get Summary Statistics of Durations ---
    # Get descriptive statistics on the calculated durations.
    time_per_respondent_under_24.reset_index(inplace = True)

    respondent_activities = df.groupby('Assignment')['Activities'].first().reset_index()

    summary_df = pd.merge(time_per_respondent_under_24, respondent_activities, on='Assignment')

    activity_stats = summary_df.groupby('Activities')['duration'].agg(
        count='size',
        mean='mean',
        p25=lambda x: x.quantile(0.25),  # 25th percentile (1st Quartile)
        median='median',                  # 50th percentile (2nd Quartile)
        p75=lambda x: x.quantile(0.75),
        min='min',
        max='max'
    )

    duration_stats = time_per_respondent_under_24['duration'].describe()

    print("\n--- Summary Statistics of Respondent Durations ---")
    print("This tells you about the distribution of time taken by all respondents.")
    

    print("\n")
    print(f"the number of responses is: {activity_stats["count"].sum()}")
    print(activity_stats)
    print(activity_stats[["p25","median", "p75"]])



    
   



except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Make sure it's in the same directory as your script.")
except Exception as e:
    print(f"An error occurred: {e}")