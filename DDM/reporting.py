import pandas as pd
import matplotlib.pyplot as plt

# Import the functions from your other two files
from analysis import load_and_clean_data
from summary_stats import print_summary_statistics

def create_table_image(main_df, time_filtered_df, analysis_name):
    """
    Creates and saves an image of the summary statistics table.
    """
    try:
        print(f"\nGenerating table image for {analysis_name}...")
        respondent_activities = main_df.groupby('Assignment')['Activities'].first().reset_index()
        summary_df = pd.merge(time_filtered_df, respondent_activities, on='Assignment')
        activity_stats = summary_df.groupby('Activities')['duration'].agg(
            count='size', mean='mean', p25=lambda x: x.quantile(0.25),
            median='median', p75=lambda x: x.quantile(0.75), min='min', max='max'
        )

        for col in ['mean', 'p25', 'median', 'p75', 'min', 'max']:
            if pd.api.types.is_timedelta64_dtype(activity_stats[col]):
                activity_stats[col] = activity_stats[col].dt.components.apply(
                    lambda x: f"{int(x.hours):02d}:{int(x.minutes):02d}:{int(x.seconds):02d}",
                    axis=1
                )
        
        df_reset = activity_stats.reset_index()
        fig, ax = plt.subplots(figsize=(16, 4))
        ax.axis('tight')
        ax.axis('off')
        the_table = ax.table(cellText=df_reset.values, colLabels=df_reset.columns, loc='center', cellLoc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        the_table.scale(1.2, 1.2)
        
        output_filename = f'summary_table_{analysis_name}.png'
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        print(f"Table image saved as '{output_filename}'")
        plt.close()

    except Exception as e:
        print(f"An error occurred while creating the table image: {e}")


def create_boxplots(main_df, time_filtered_df, analysis_name):
    """
    Generates and saves a boxplot of completion times grouped by activity.
    """
    try:
        print(f"\nGenerating boxplot for {analysis_name}...")
        respondent_activities = main_df.groupby('Assignment')['Activities'].first().reset_index()
        plot_df = pd.merge(time_filtered_df, respondent_activities, on='Assignment')
        
        plot_df['duration'] = pd.to_timedelta(plot_df['duration'])
        plot_df['duration_minutes'] = plot_df['duration'].dt.total_seconds() / 60

        plt.figure(figsize=(12, 8))
        plot_df.boxplot(column='duration_minutes', by='Activities', vert=False)
        
        plt.title(f'Completion Time by Test Form ({analysis_name})')
        plt.xlabel('Completion Time (Minutes)')
        plt.ylabel('Test Form')
        plt.suptitle('')
        plt.tight_layout()

        output_filename = f'completion_time_boxplot_{analysis_name}.png'
        plt.savefig(output_filename)
        print(f"Boxplot saved as '{output_filename}'")
        plt.close()

    except Exception as e:
        print(f"An error occurred while creating the plot: {e}")


def create_histograms(time_filtered_df, analysis_name):
    """
    Generates and saves a histogram of completion times.
    """
    try:
        print(f"\nGenerating histogram for {analysis_name}...")
        duration_minutes = pd.to_timedelta(time_filtered_df['duration']).dt.total_seconds() / 60
        
        max_minutes = 120 
        bin_interval = 5
        bins = range(0, max_minutes + bin_interval, bin_interval)

        plt.figure(figsize=(12, 8))
        plt.hist(duration_minutes, bins=bins, edgecolor='black')
        
        plt.title(f'Distribution of Completion Times ({analysis_name})')
        plt.xlabel('Completion Time (Minutes)')
        plt.ylabel('Number of Respondents')
        plt.xticks(bins)
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()

        output_filename = f'completion_time_histogram_{analysis_name}.png'
        plt.savefig(output_filename)
        print(f"Histogram saved as '{output_filename}'")
        plt.close()

    except Exception as e:
        print(f"An error occurred while creating the histogram: {e}")

# --- Main execution block ---
if __name__ == "__main__":

    # --- DEFINE YOUR DATASET CONFIGURATIONS HERE ---
    datasets_to_process = [
        {
            'analysis_name': 'HS_NoPauses',
            'file_path': 'Spring 2025 DDM HS Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 DDM HS Administration',
            'filter_pauses': True  # Filters out pauses
        },
        {
            'analysis_name': 'MS_NoPauses',
            'file_path': 'Spring 2025 MS DDM Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 MS DDM Administration',
            'filter_pauses': True  # Filters out pauses
        },
        {
            'analysis_name': 'HS_WithPauses',
            'file_path': 'Spring 2025 DDM HS Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 DDM HS Administration',
            'filter_pauses': False # Includes pauses
        },
        {
            'analysis_name': 'MS_WithPauses',
            'file_path': 'Spring 2025 MS DDM Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 MS DDM Administration',
            'filter_pauses': False # Includes pauses
        }
    ]

    # Loop through and process each dataset
    for config in datasets_to_process:
        print("\n" + "="*70)
        print(f"Starting Analysis: {config['analysis_name']}")
        print(f"File: {config['file_path']}")
        
        main_df, time_filtered_df = load_and_clean_data(config)
        
        if main_df is not None and time_filtered_df is not None:
            # Print the text tables to the console
            print(f"\n--- Summary Statistics for {config['analysis_name']} ---")
            print_summary_statistics(main_df, time_filtered_df)
            
            # Create and save the table as an image
            create_table_image(main_df, time_filtered_df, config['analysis_name'])
            
            # Create and save the boxplot as an image
            create_boxplots(main_df, time_filtered_df, config['analysis_name'])
            
            # Create and save the histogram as an image
            create_histograms(time_filtered_df, config['analysis_name'])