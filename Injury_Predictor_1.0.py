# Import necessary libraries
import pandas as pd
import streamlit as st
import altair as alt

# Streamlit App Title
st.title("NBA Injury Predictor by Position")
st.image("images/nbapic4.jpg", caption="Amar'e Stoudemire - Knicks", use_container_width=True)


# Define available players and their corresponding CSVs
positions = {
    "Point Guard": {
        "Derrick Rose": "data/Derrick_Rose_Stats.csv",
        "Jamal Murray": "data/Jamal_Murray_Stats.csv",
        "Rajon Rondo": "data/Rajon_Rondo_Stats.csv",
        "Shaun Livingston": "data/Shaun_Livingston_Stats.csv",
        "Dante Exum": "data/Dante_Exum_Stats.csv",
    },
    "Shooting Guard": {
        "Kobe Bryant": "data/Kobe_Bryant_Stats.csv",
        "Wesley Matthews": "data/Wesley_Matthews_Stats.csv",
        "Brandon Jennings": "data/Brandon_Jennings_Stats.csv",
        "Rodney Hood": "data/Rodney_Hood_Stats.csv",
    },
    "Small Forward": {
        "Kawhi Leonard": "data/Kawhi_Leonard_Stats.csv",
        "Jimmy Butler": "data/Jimmy_Butler_Stats.csv",
        "Danilo Gallinari": "data/Danilo_Gallinari_Stats.csv",
        "Otto Porter Jr.": "data/Otto_Porter_Stats.csv",
    },
    "Power Forward": {
        "Blake Griffin": "data/Blake_Griffin_Stats.csv",
        "Kevin Love": "data/Kevin_Love_Stats.csv",
        "Anthony Davis": "data/Anthony_Davis_Stats.csv",
        "Amar’e Stoudemire": "data/Amare_Stoudemire_Stats.csv",
    },
    "Center": {
        "Yao Ming": "data/Yao_Ming_Stats.csv",
        "Bill Walton": "data/Bill_Walton_Stats.csv",
        "Zydrunas Ilgauskas": "data/Zydrunas_Ilgauskas_Stats.csv",
    },
}

# Step 1: Select Position
selected_position = st.selectbox("Select Position:", list(positions.keys()))

if selected_position:
    # Step 2: Load All Players for the Position
    players = positions[selected_position]
    dataframes = []
    injury_years = {}

    for player_name, file_path in players.items():
        try:
            # Load each player's data
            df = pd.read_csv(file_path)

            # Allow user to input injury year for the player
            injury_year = st.number_input(
                f"Enter the injury year for {player_name}:", min_value=1900, max_value=2100, step=1
            )
            injury_years[player_name] = injury_year

            # Add player name column
            df["Player"] = player_name
            dataframes.append(df)
        except FileNotFoundError:
            st.error(f"File for {player_name} not found.")

    # Combine all data for the position
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Standardize column names
    combined_df.columns = combined_df.columns.str.strip().str.lower()

    # Clean the data
    combined_df.replace("Did not play", pd.NA, inplace=True)

    # Convert numeric columns to proper types
    numeric_cols = [
        "g", "gs", "mp", "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%",
        "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pf", "pts"
    ]
    combined_df[numeric_cols] = combined_df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Drop rows with missing games or points
    combined_df.dropna(subset=["g", "pts"], inplace=True)

    # Filter out seasons with fewer than the minimum games played
    min_games_played = st.slider("Set Minimum Games Played to Include a Season:", min_value=1, max_value=82, value=65)
    st.image("images/nbapic3.jpg", caption="Jimmy Butler - Heat", use_container_width=True)  # Image after slider

    combined_df = combined_df[combined_df["g"] >= min_games_played]

    # Add Pre- and Post-Injury Labels
    combined_df["injury_status"] = combined_df.apply(
        lambda row: "Pre-Injury" if int(row["season"][:4]) < injury_years.get(row["player"], 9999) else "Post-Injury",
        axis=1
    )

    # Analyze On-Court Stats
    on_court_stats = [
        "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%",
        "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pts"
    ]
    combined_stats = combined_df.groupby("injury_status")[on_court_stats].mean()

    # Calculate total changes
    total_changes = combined_stats.loc["Post-Injury"] - combined_stats.loc["Pre-Injury"]

    # Identify the stat with the greatest total change
    most_changed_stat = total_changes.abs().idxmax()
    max_total_change = total_changes[most_changed_stat]
    change_direction = "increased" if max_total_change > 0 else "decreased"

    # Display Results
    st.subheader(f"Combined Pre/Post-Injury On-Court Averages for {selected_position}")
    st.dataframe(combined_stats)

   
    st.subheader(f"Total Changes (Post-Injury - Pre-Injury) for {selected_position}")
    st.dataframe(total_changes)

    st.markdown(f"**Statistic with the most total change:** {most_changed_stat}")
    st.markdown(f"**Total Change Value:** {max_total_change:.2f} ({change_direction})")
    
    st.image("images/nbapic2.jpg", caption="Kawhi Leonard - Raptors", use_container_width=True)  # Before visualizations

   # Visualizations
import altair as alt

# Prepare data for visualization
combined_stats_melted = combined_stats.reset_index().melt(id_vars="injury_status", var_name="Statistic", value_name="Value")

# Create a side-by-side bar chart
side_by_side_chart = alt.Chart(combined_stats_melted).mark_bar().encode(
    x=alt.X("Statistic:N", title="Statistic"),
    y=alt.Y("Value:Q", title="Value"),
    color=alt.Color("injury_status:N", title="Injury Status"),
    column=alt.Column("injury_status:N", title=None, spacing=5)
).properties(
    width=300,  # Adjust width for better appearance
    height=400
)

st.altair_chart(side_by_side_chart)



# Add bottom image
st.image("images/nbapic1.jpg", caption="Kobe Bryant - Lakers", use_container_width=True)
