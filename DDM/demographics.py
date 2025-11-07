import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import textwrap

# --- Configuration (Using XLSX files and sheet names) ---
HS_EXCEL_FILE = 'Spring 2025 DDM HS Administration answers.xlsx'
HS_DATA_SHEET = 'Spring 2025 DDM HS Administrati' # The data tab
HS_VARLIST_SHEET = 'varlist'                      # The varlist tab

MS_EXCEL_FILE = 'Spring 2025 MS DDM Administration answers.xlsx'
MS_DATA_SHEET = 'Spring 2025 MS DDM Administrati' # The data tab
MS_VARLIST_SHEET = 'varlist'                      # The varlist tab

# Variables to summarize
HS_DEMOGRAPHIC_VARS = ['D.03_HSgrade_level', 'D.05_gender', 'race.ethn.r', 'D.10_Native_Language', 'D.11_APcourses', 'D.12_IB']
MS_DEMOGRAPHIC_VARS = ['D.04_MSgrade_level', 'D.05_gender', 'race.ethn.r', 'D.15_Native_Language', 'D.16_ELL']

# STEM perception variables
HS_STEM_VARS = {
    'D.13_STEM_perception 1': 'Confident to be successful in STEM courses',
    'D.13_STEM_perception 2': 'Interest in more challenging STEM courses',
    'D.13_STEM_perception 3': 'Many STEM opportunities at school',
    'D.13_STEM_perception 4': 'Interest in STEM career options after HS'
}
MS_STEM_VARS = {
    'STEM.perception 1': 'Confident to be successful in STEM courses',
    'STEM.perception 2': 'Interest in more challenging STEM courses',
    'STEM.perception 3': 'Many STEM opportunities at school',
    'STEM.perception 4': 'Interest in STEM career options after HS'
}

# --- Helper Functions ---

def parse_key(key_string):
    """Parses the 'possible values' string into a dictionary."""
    if pd.isna(key_string):
        return None
    try:
        key_dict = {}
        matches = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*"([^"]*)"', str(key_string))
        for key, value in matches:
            key_dict[key.strip()] = value.strip()
        
        if not key_dict:
            for item in str(key_string).split('\n'):
                parts = item.split(':', 1)
                if len(parts) == 2:
                    key_dict[parts[0].strip()] = parts[1].strip().strip('"')
                    
        return key_dict
    except Exception as e:
        print(f"Error parsing key string: {e}, {key_string}")
        return None

def create_race_variable(df, hispanic_var='D.08_hispanic_YN', race_var='D.09_Race_ethnicity'):
    """
    Creates the combined 'race.ethn.r' variable.
    It maps the race variable, then overrides with 'Hispanic' if D.08 is 'Yes'.
    """
    race_map = {
        'a': 'American Indian or Other Native American',
        'b': 'Asian American or Pacific Islander',
        'c': 'Black or African American',
        'd': 'White',
        'e': 'Multi-racial',
        'f': 'Prefer not to answer'
    }
    
    if race_var not in df.columns or hispanic_var not in df.columns:
        print(f"Warning: Race/ethnicity columns ({race_var}, {hispanic_var}) not found. Skipping.")
        df['race.ethn.r'] = 'Data Not Available'
        return df

    df['race.ethn.r'] = df[race_var].map(race_map)
    df.loc[df[hispanic_var] == 'a', 'race.ethn.r'] = 'Hispanic'
    df['race.ethn.r'] = df['race.ethn.r'].fillna('Unknown')
    
    return df

def summarize_variable(df, varlist_df, var_name):
    """
    Generates and prints a formatted summary table for a given variable.
    """
    if var_name not in df.columns:
        print(f"\n--- WARNING: Variable '{var_name}' not found in data ---")
        return

    try:
        var_info = varlist_df.loc[var_name]
    except KeyError:
        print(f"\n--- NOTE: Variable '{var_name}' not in varlist (likely custom). ---")
        var_info = {}
    
    description = var_info.get('description', var_name)
    key_col_name = 'possible values' if 'possible values' in var_info else 'key'
    key_dict = parse_key(var_info.get(key_col_name))

    print("\n" + "="*50)
    print(f"Variable: {var_name}")
    print(f"Description: {description}")
    print("="*50)

    if "Select all that apply" in str(description) and key_dict:
        all_responses = df[var_name].astype(str).dropna().str.split(',')
        all_options = []
        for response_list in all_responses:
            all_options.extend(response_list)
        
        counts = pd.Series(all_options).value_counts()
        percentages = (counts / len(all_responses)) * 100
        label_map = {k: f"{v} ({k})" for k, v in key_dict.items()}
        
        summary_table = pd.DataFrame({'Label': counts.index.map(label_map).fillna('Unknown Key'), 
                                      'Count': counts, 
                                      'Percentage': percentages})
        print(summary_table.to_string())
        print(f"Total respondents (N) = {len(all_responses)}")
    
    else:
        counts = df[var_name].value_counts()
        percentages = df[var_name].value_counts(normalize=True) * 100
        
        summary_table = pd.DataFrame({'Count': counts, 'Percentage': percentages})
        
        if key_dict:
            summary_table['Label'] = summary_table.index.map(key_dict).fillna('Other/Text')
            summary_table = summary_table.set_index('Label')
        elif var_name == 'race.ethn.r':
            pass
        else:
            total_count = summary_table['Count'].sum()
            top_responses = summary_table.head(10)
            other_count = summary_table['Count'][10:].sum()
            
            if other_count > 0:
                other_row = pd.DataFrame({'Count': [other_count], 'Percentage': [(other_count/total_count)*100]}, index=['Other (Recategorized)'])
                summary_table = pd.concat([top_responses, other_row])
                
        print(summary_table.to_string())
        print(f"Total respondents (N) = {counts.sum()}")

# --- THIS FUNCTION IS MODIFIED ---
def plot_stem_perception(df, stem_vars_map, school_level):
    """
    Generates and saves the stacked bar chart for STEM perception
    with percentage labels inside each segment.
    """
    print(f"\n--- Generating STEM Perception Plot for {school_level} ---")
    
    answer_map = {
        'a': 'Describes me exactly',
        'b': 'Mostly describes me',
        'c': 'Describes me a little bit',
        'd': 'Definitely does not describe me',
        'e': 'Prefer not to answer'
    }
    
    vars_to_plot = [v for v in stem_vars_map.keys() if v in df.columns]
    if not vars_to_plot:
        print(f"--- WARNING: No STEM perception variables found for {school_level}. Skipping plot. ---")
        return
        
    stem_df = df[vars_to_plot].rename(columns=stem_vars_map)
    df_melted = stem_df.melt(var_name='Question', value_name='Answer Code')
    df_melted['Answer'] = df_melted['Answer Code'].map(answer_map).fillna('No Answer')
    summary = df_melted.groupby('Question')['Answer'].value_counts(normalize=True).unstack() * 100
    
    categories = ['Describes me exactly', 'Mostly describes me', 'Describes me a little bit', 'Definitely does not describe me', 'Prefer not to answer', 'No Answer']
    for cat in categories:
        if cat not in summary.columns:
            summary[cat] = 0
    summary = summary[categories]
    
    ax = summary.plot(
        kind='barh', 
        stacked=True, 
        figsize=(12, 6),
        colormap='Blues_r',  # <-- THIS LINE IS CHANGED
        title=f'STEM Perceptions ({school_level})'
    )
    
    # Add percentage labels inside bars
    for container in ax.containers:
        # Only show label if the percentage is > 5% to avoid clutter
        labels = [f'{v:.1f}%' if v > 5 else '' for v in container.datavalues]
        
        ax.bar_label(
            container,
            labels=labels,
            label_type='center',
            color='white',
            fontsize=8,
            fontweight='bold'
        )
    
    ax.set_yticklabels([textwrap.fill(label, 30) for label in summary.index])
    ax.set_xlabel('Percentage')
    ax.set_ylabel('')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    output_filename = f'stem_perception_{school_level}.png'
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    print(f"STEM perception plot saved as '{output_filename}'")

# --- Main Analysis ---

def run_hs_analysis(excel_file, data_sheet, varlist_sheet):
    """Runs the full analysis for High School data."""
    print("#" * 70)
    print("# HIGH SCHOOL DEMOGRAPHIC SUMMARY")
    print("#" * 70)
    
    try:
        df = pd.read_excel(excel_file, sheet_name=data_sheet)
        varlist_df = pd.read_excel(excel_file, sheet_name=varlist_sheet, index_col='variable')
    except Exception as e:
        print(f"Error loading Excel file '{excel_file}': {e}")
        return

    df = create_race_variable(df)
    
    # Create a DataFrame unique by Student ID
    df_unique_students = df.drop_duplicates(subset=['Student'])
    
    # --- Run Overall Summary (using the unique student df) ---
    print(f"\n--- OVERALL HS SUMMARY (N={len(df_unique_students)}) ---")
    for var in HS_DEMOGRAPHIC_VARS:
        summarize_variable(df_unique_students, varlist_df, var)
        
    # --- Run By Course Summary (using the original df) ---
    print("\n" + "#" * 70)
    print("# HIGH SCHOOL SUMMARY (BY AP COURSE)")
    print("#" * 70)

    course_demo_vars = ['D.03_HSgrade_level', 'D.05_gender', 'race.ethn.r', 'D.10_Native_Language']
    
    try:
        ap_key_dict = parse_key(varlist_df.loc['D.11_APcourses'].get('possible values'))
    except KeyError:
        print("--- WARNING: 'D.11_APcourses' not found in varlist. Skipping 'By Course' summary. ---")
        ap_key_dict = None
    
    if ap_key_dict:
        df['D.11_APcourses'] = df['D.11_APcourses'].astype(str)
        
        for key, label in ap_key_dict.items():
            group_df = df[df['D.11_APcourses'].str.contains(key, na=False)]
            group_df_unique = group_df.drop_duplicates(subset=['Student'])
            
            print("\n" + "*" * 70)
            print(f"SUMMARY FOR STUDENTS WHO TOOK: {label} (N={len(group_df_unique)})")
            print("*" * 70)
            
            if len(group_df_unique) < 10:
                print("--- Skipping course, too few respondents ---")
                continue
            
            for var in course_demo_vars:
                summarize_variable(group_df_unique, varlist_df, var)
    else:
        print("--- WARNING: Could not parse AP Course keys. Skipping 'By Course' summary. ---")

    # --- Generate HS STEM Plot (using the unique student df) ---
    plot_stem_perception(df_unique_students, HS_STEM_VARS, 'HS')

def run_ms_analysis(excel_file, data_sheet, varlist_sheet):
    """Runs the 'overall only' analysis for Middle School data."""
    print("\n" + "#" * 70)
    print("# MIDDLE SCHOOL DEMOGRAPHIC SUMMARY (OVERALL)")
    print("#" * 70)
    
    try:
        df = pd.read_excel(excel_file, sheet_name=data_sheet)
        varlist_df = pd.read_excel(excel_file, sheet_name=varlist_sheet, index_col='variable')
    except Exception as e:
        print(f"Error loading Excel file '{excel_file}': {e}")
        return

    df = create_race_variable(df)
    
    # Create a DataFrame unique by Student ID
    df_unique_students = df.drop_duplicates(subset=['Student'])

    # --- Run Overall Summary (using the unique student df) ---
    print(f"\n--- (N={len(df_unique_students)}) ---")
    for var in MS_DEMOGRAPHIC_VARS:
        summarize_variable(df_unique_students, varlist_df, var)
        
    # --- Generate MS STEM Plot (using the unique student df) ---
    plot_stem_perception(df_unique_students, MS_STEM_VARS, 'MS')

# --- Main execution ---
if __name__ == "__main__":
    
    # Run High School Analysis
    run_hs_analysis(HS_EXCEL_FILE, HS_DATA_SHEET, HS_VARLIST_SHEET)
    
    # Run Middle School Analysis
    run_ms_analysis(MS_EXCEL_FILE, MS_DATA_SHEET, MS_VARLIST_SHEET)
    
    print("\n" + "="*70)
    print("Demographic analysis complete.")
    print("Output tables are above. PNG plots have been saved to the folder.")
    print("="*70)