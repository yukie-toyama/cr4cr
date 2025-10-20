import pandas as pd
from tabulate import tabulate

def print_summary_statistics(main_df, time_filtered_df):
    """
    Calculates and prints summary statistics for respondent durations,
    grouped by activity.

    Args:
        main_df (pd.DataFrame): The cleaned DataFrame with all respondent actions.
        time_filtered_df (pd.DataFrame): The DataFrame containing only respondents
                                         who finished within the time limits.
    """
    try:
        # Get the activity for each respondent from the main dataframe
        respondent_activities = main_df.groupby('Assignment')['Activities'].first().reset_index()

        # Merge the time-filtered data with the activity names
        summary_df = pd.merge(time_filtered_df, respondent_activities, on='Assignment')

        # --- Calculate Summary Statistics ---
        activity_stats = summary_df.groupby('Activities')['duration'].agg(
            count='size',
            mean='mean',
            p25=lambda x: x.quantile(0.25),
            median='median',
            p75=lambda x: x.quantile(0.75),
            min='min',
            max='max'
        )

        print("\n--- Summary Statistics of Respondent Durations ---")
        print("This table shows the distribution of time taken by all respondents, grouped by form.")
        
        # --- Print the Tables ---
        print(f"\nTotal number of valid responses: {activity_stats['count'].sum()}")
        
        # Print a nicely formatted table using the 'tabulate' library
        print("\n--- Full Summary Table ---")
        print(tabulate(activity_stats, headers='keys', tablefmt='psql'))
        
        print("\n--- Quantile Summary ---")
        print(tabulate(activity_stats[["p25", "median", "p75"]], headers='keys', tablefmt='psql'))

    except Exception as e:
        print(f"An error occurred in the statistics module: {e}")