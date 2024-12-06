# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Manually Load Each CSV File
derrick_rose_df = pd.read_csv('C:/Users/drako/OneDrive/Desktop/Jake Professional/Projects/CTP Basketball/Derrick_Rose_Stats.csv')
klay_thompson_df = pd.read_csv('C:/Users/drako/OneDrive/Desktop/Jake Professional/Projects/CTP Basketball/Klay_Thompson_Stats.csv')
jamal_murray_df = pd.read_csv('C:/Users/drako/OneDrive/Desktop/Jake Professional/Projects/CTP Basketball/Jamal_Murray_Stats.csv')
rajon_rondo_df = pd.read_csv('C:/Users/drako/OneDrive/Desktop/Jake Professional/Projects/CTP Basketball/Rajon_Rondo_Stats.csv')
ricky_rubio_df = pd.read_csv('C:/Users/drako/OneDrive/Desktop/Jake Professional/Projects/CTP Basketball/Ricky_Rubio_Stats.csv')

# Step 2: Add Player Names to Each DataFrame
derrick_rose_df["Player"] = "Derrick Rose"
klay_thompson_df["Player"] = "Klay Thompson"
jamal_murray_df["Player"] = "Jamal Murray"
rajon_rondo_df["Player"] = "Rajon Rondo"
ricky_rubio_df["Player"] = "Ricky Rubio"

# Step 3: Combine All DataFrames
combined_df = pd.concat([derrick_rose_df, klay_thompson_df, jamal_murray_df, ricky_rubio_df, rajon_rondo_df])

# Standardize column names
combined_df.columns = combined_df.columns.str.strip().str.lower()

# Step 4: Clean the Data
# Replace "Did not play" with NaN
combined_df.replace("Did not play", pd.NA, inplace=True)

# Convert numeric columns to proper types
numeric_cols = [
    "g", "gs", "mp", "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%", 
    "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pf", "pts"
]
combined_df[numeric_cols] = combined_df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# Drop rows with missing games or points
combined_df.dropna(subset=["g", "pts"], inplace=True)

# Filter out specific seasons where players played fewer than the minimum games
min_games_played = 65  # Set your threshold for games played
combined_df = combined_df[combined_df["g"] >= min_games_played]


# Step 5: Add Pre- and Post-Injury Labels
injury_years = {
    "derrick rose": 2012,
    "klay thompson": 2019,
    "jamal murray": 2021,
    "rajon rondo" : 2013,
    "ricky rubio": 2012
}

combined_df["injury_status"] = combined_df.apply(
    lambda row: "Pre-Injury" if int(row["season"][:4]) < injury_years.get(row["player"].lower(), 9999) else "Post-Injury",
    axis=1
)

# Step 6: Analyze the Data (Combined On-Court Stats Only)
# Select only on-court performance stats
on_court_stats = [
    "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%", 
    "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pts"
]


# Calculate combined averages for pre- and post-injury
combined_stats = combined_df.groupby("injury_status")[on_court_stats].mean()

# Calculate total changes instead of percentage changes
absolute_changes = combined_stats.loc["Post-Injury"] - combined_stats.loc["Pre-Injury"]

# Identify the stat with the greatest total change
most_changed_stat = absolute_changes.abs().idxmax()
max_total_change = absolute_changes[most_changed_stat]  # Get the actual total change value

# Determine if the change is positive or negative
change_direction = "increased" if max_total_change > 0 else "decreased"

# Display the results
print("\nCombined Pre/Post-Injury On-Court Averages:")
print(combined_stats)
print("\nTotal Changes (Post-Injury - Pre-Injury):")
print(absolute_changes)
print(f"\nStatistic with the most total change: {most_changed_stat}")
print(f"Total Change Value: {max_total_change:.2f} ({change_direction})")

# Visualize Combined Averages for All Players
combined_stats.T.plot(kind="bar", figsize=(14, 8))  # Transpose to show stats on the X-axis
plt.title("Combined Average On-Court Stats: Pre-Injury vs. Post-Injury")
plt.xlabel("Statistics")
plt.ylabel("Average Value")
plt.xticks(rotation=45)
plt.legend(title="Injury Status", loc="upper right")
plt.tight_layout()
plt.show()

# Visualize Total Changes
absolute_changes.plot(kind="bar", figsize=(14, 6), color='orange')
plt.title("Total Changes in On-Court Stats: Post-Injury vs. Pre-Injury")
plt.xlabel("Statistics")
plt.ylabel("Total Change (Post-Injury - Pre-Injury)")
plt.xticks(rotation=45)
plt.axhline(0, color="black", linewidth=1, linestyle="--")
plt.tight_layout()
plt.show()
