import pandas as pd
import matplotlib.pyplot as plt

# Import the functions from your other two files
from analysis import load_and_clean_data
from summary_stats import print_summary_statistics

def create_boxplots(summary_df, time_filtered_df):
    """
    Generates and saves a boxplot of completion times grouped by activity.
    """
    try:
        # Merge the time-filtered data with activity names to prepare for plotting
        respondent_activities = summary_df.groupby('Assignment')['Activities'].first().reset_index()
        plot_df = pd.merge(time_filtered_df, respondent_activities, on='Assignment')

        plot_df['duration'] = pd.to_timedelta(plot_df['duration'])

        # Convert duration to total minutes for easier plotting
        plot_df['duration_minutes'] = plot_df['duration'].dt.total_seconds() / 60

        print("\nGenerating boxplot...")

        # Create the boxplot
        plt.figure(figsize=(12, 8))
        plot_df.boxplot(column='duration_minutes', by='Activities', vert=False)
        
        plt.title('Completion Time by Test Form')
        plt.xlabel('Completion Time (Minutes)')
        plt.ylabel('Test Form')
        plt.suptitle('') # Suppress the default title
        plt.tight_layout()

        # Save the plot as an image file
        plt.savefig('completion_time_boxplot.png')
        print("Boxplot saved as 'completion_time_boxplot.png'")
        
        # To display the plot when running interactively (optional)
        # plt.show()

    except Exception as e:
        print(f"An error occurred while creating the plot: {e}")


# --- Main execution block ---
if __name__ == "__main__":
    file_path = 'Spring 2025 MS DDM Administration respondent actions.csv'
    
    # 1. Load and clean the data using the function from analysis.py
    main_df, time_filtered_df = load_and_clean_data(file_path)
    
    if main_df is not None and time_filtered_df is not None:
        # 2. Print the summary tables using the function from statistics.py
        print_summary_statistics(main_df, time_filtered_df)
        
        # 3. Create and save the boxplots using the function in this file
        create_boxplots(main_df, time_filtered_df)