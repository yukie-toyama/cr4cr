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

# --- THIS FUNCTION IS MODIFIED ---
def create_boxplots(main_df, time_filtered_df, analysis_name):
    """
    Generates and saves a boxplot of completion times, including
    a 1-hour mark and the labeled mean for each test form.
    """
    try:
        print(f"\nGenerating boxplot for {analysis_name}...")
        respondent_activities = main_df.groupby('Assignment')['Activities'].first().reset_index()
        plot_df = pd.merge(time_filtered_df, respondent_activities, on='Assignment')
        
        plot_df['duration'] = pd.to_timedelta(plot_df['duration'])
        plot_df['duration_minutes'] = plot_df['duration'].dt.total_seconds() / 60

        # --- MODIFICATIONS START HERE ---
        
        # 1. Create a Figure and Axis explicitly
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 2. Tell the boxplot to use this axis
        plot_df.boxplot(column='duration_minutes', by='Activities', vert=False, ax=ax)

        # 3. Calculate the mean for each group
        group_means = plot_df.groupby('Activities')['duration_minutes'].mean()
        
        # 4. Get the y-axis positions and labels from the plot
        y_ticks = ax.get_yticks()
        y_labels = [item.get_text() for item in ax.get_yticklabels()]
        
        # 5. Re-order the means to match the plot's y-axis
        ordered_means = group_means.reindex(y_labels)

        # 6. Plot the means as vertical red ticks
        ax.plot(ordered_means, y_ticks, 
                marker='|',         # Use a vertical line marker
                color='red',        # Set color to red
                markersize=10,      # Control the length of the line
                markeredgewidth=3,  # Control the thickness of the line
                linestyle='None',   # Don't connect the markers
                label='Mean')       # Add to the legend
        
        # 7. Add the text labels next to each mean
        for mean_val, y_pos in zip(ordered_means, y_ticks):
            # Format the text (e.g., "25.3")
            text_label = f'{mean_val:.1f}'
            
            # Add the text with a small horizontal offset
            ax.text(x=mean_val + 0.5,   # X position (mean + 0.5 min offset)
                    y=y_pos - 0.2,            # Y position (matches the box)
                    s=text_label,       # The text to display
                    color='red',        # Color of the text
                    va='center',        # Vertical alignment
                    ha='left',          # Horizontal alignment
                    fontsize=9)         # Font size
        
        # 8. Add the 1-hour (60 minutes) line
        ax.axvline(x=60, color='blue', linestyle='--', linewidth=2, label='1 Hour (60 min)')
        
        # 9. Add a legend
        ax.legend()
        
        # --- MODIFICATIONS END HERE ---

        plt.title(f'Completion Time by Test Form ({analysis_name})')
        plt.xlabel('Completion Time (Minutes)')
        plt.ylabel('Test Form')
        plt.suptitle('') # Suppress the default title
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

# --- Main execution block (no changes needed here) ---
if __name__ == "__main__":

    datasets_to_process = [
        {
            'analysis_name': 'HS_NoPauses',
            'file_path': 'Spring 2025 DDM HS Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 DDM HS Administration',
            'filter_pauses': True
        },
        {
            'analysis_name': 'MS_NoPauses',
            'file_path': 'Spring 2025 MS DDM Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 MS DDM Administration',
            'filter_pauses': True
        },
        {
            'analysis_name': 'HS_WithPauses',
            'file_path': 'Spring 2025 DDM HS Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 DDM HS Administration',
            'filter_pauses': False
        },
        {
            'analysis_name': 'MS_WithPauses',
            'file_path': 'Spring 2025 MS DDM Administration respondent actions.csv',
            'complete_action': 'End activity Spring 2025 MS DDM Administration',
            'filter_pauses': False
        }
    ]

    for config in datasets_to_process:
        print("\n" + "="*70)
        print(f"Starting Analysis: {config['analysis_name']}")
        print(f"File: {config['file_path']}")
        
        main_df, time_filtered_df = load_and_clean_data(config)
        
        if main_df is not None and time_filtered_df is not None:
            print(f"\n--- Summary Statistics for {config['analysis_name']} ---")
            print_summary_statistics(main_df, time_filtered_df)
            
            create_table_image(main_df, time_filtered_df, config['analysis_name'])
            
            create_boxplots(main_df, time_filtered_df, config['analysis_name'])
            
            create_histograms(time_filtered_df, config['analysis_name'])