import pandas as pd 
from datetime import datetime

#  CONFIG 
filename = "Spring 2025 CoT HS Administration respondent actions - Spring 2025 CoT HS Administration respondent actions.csv"
time_format = "%m/%d/%Y %H:%M:%S"  # adjust if needed

# LOAD CSV INTO DATAFRAME 
df = pd.read_csv(filename)

# Merge Date + Time into one column
df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format=time_format)

# Identify pause users 
pause_flags = df.groupby(["Assignment","Activities"])["Action"].apply(
    lambda x: any("Pause activity" in a for a in x)
).reset_index(name="HasPause")

# Get start/end times 
def get_times(group):
    start = group.loc[group["Action"].str.contains("Begin activity"), "DateTime"].min()
    end = group.loc[group["Action"].str.contains("End activity"), "DateTime"].max()
    return pd.Series({"Start": start, "End": end})

times = df.groupby(["Assignment","Activities"]).apply(get_times).reset_index()
times["Duration"] = times["End"] - times["Start"]

#  Keep only same-day exams 
times = times[times["Start"].dt.date == times["End"].dt.date]

# Merge and subset no-pause
merged = times.merge(pause_flags, on=["Assignment","Activities"])
no_pause = merged[merged["HasPause"] == False]

# Compute summary stats 
def duration_summary(x):
    return pd.Series({
        "Mean": x.mean(),
        "SD": x.std(),
        "Min": x.min(),
        "Max": x.max(),
        "Median": x.median(),
        "n": x.count(),
        "P25": x.quantile(0.25),
        "P75": x.quantile(0.75),
        "P90": x.quantile(0.90)
    })

summary = (
    no_pause.groupby(["Activities"])["Duration"]
    .apply(duration_summary)
    .reset_index()
)

# --- Save to CSV ---
output_file = "no_pause_summary_full.csv"
summary.to_csv(output_file, index=False)

print(f"✅ Saved full summary with percentiles to {output_file}")