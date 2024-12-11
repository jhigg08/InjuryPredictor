# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit App Title
st.title("NBA Injury Predictor by Position")

# Predefined player data by position
position_data = {
    "Point Guard": {
        "players": {
            "Derrick Rose": {"file": "Derrick_Rose_Stats.csv", "injury_year": 2012},
            "Jamal Murray": {"file": "Jamal_Murray_Stats.csv", "injury_year": 2021},
            "Rajon Rondo": {"file": "Rajon_Rondo_Stats.csv", "injury_year": 2013},
            "Shaun Livingston": {"file": "Shaun_Livingston_Stats.csv", "injury_year": 2007},
            "Dante Exum": {"file": "Dante_Exum_Stats.csv", "injury_year": 2015},
        }
    },
    "Shooting Guard": {
        "players": {
            "Kobe Bryant": {"file": "Kobe_Bryant_Stats.csv", "injury_year": 2013},
            "Wesley Matthews": {"file": "Wesley_Matthews_Stats.csv", "injury_year": 2015},
            "Brandon Jennings": {"file": "Brandon_Jennings_Stats.csv", "injury_year": 2015},
            "Rodney Hood": {"file": "Rodney_Hood_Stats.csv", "injury_year": 2019},
        }
    },
    "Small Forward": {
        "players": {
            "Kawhi Leonard": {"file": "Kawhi_Leonard_Stats.csv", "injury_year": 2021},
            "Jimmy Butler": {"file": "Jimmy_Butler_Stats.csv", "injury_year": 2015},
            "Danilo Gallinari": {"file": "Danilo_Gallinari_Stats.csv", "injury_year": 2013},
            "Otto Porter Jr.": {"file": "Otto_Porter_Stats.csv", "injury_year": 2018},
        }
    },
    "Power Forward": {
        "players": {
            "Blake Griffin": {"file": "Blake_Griffin_Stats.csv", "injury_year": 2016},
            "Kevin Love": {"file": "Kevin_Love_Stats.csv", "injury_year": 2012},
            "Anthony Davis": {"file": "Anthony_Davis_Stats.csv", "injury_year": 2013},
            "Amar’e Stoudemire": {"file": "Amare_Stoudemire_Stats.csv", "injury_year": 2012},
        }
    },
    "Center": {
        "players": {
            "Yao Ming": {"file": "Yao_Ming_Stats.csv", "injury_year": 2008},
            "Bill Walton": {"file": "Bill_Walton_Stats.csv", "injury_year": 1978},
            "Zydrunas Ilgauskas": {"file": "Zydrunas_Ilgauskas_Stats.csv", "injury_year": 1998},
        }
    }
}

# Dropdown for position selection
selected_position = st.selectbox("Select a position to analyze:", position_data.keys())

if selected_position:
    # Load players for the selected position
    players = position_data[selected_position]["players"]
    dataframes = []

    # Process data for each player
    for player_name, player_data in players.items():
        file_path = f"data/{player_data['file']}"
        injury_year = player_data["injury_year"]

        try:
            df = pd.read_csv(file_path)
            df["Player"] = player_name
            df["Injury Status"] = df.apply(
                lambda row: "Pre-Injury" if int(row["season"][:4]) < injury_year else "Post-Injury",
                axis=1
            )
            dataframes.append(df)
        except FileNotFoundError:
            st.error(f"File not found for {player_name}: {file_path}")
            continue

    # Combine data for all players in the selected position
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Standardize column names
    combined_df.columns = combined_df.columns.str.strip().str.lower()

    # Clean data
    combined_df.replace("Did not play", pd.NA, inplace=True)
    numeric_cols = [
        "g", "gs", "mp", "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%",
        "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pf", "pts"
    ]
    combined_df[numeric_cols] = combined_df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    combined_df.dropna(subset=["g", "pts"], inplace=True)

    # Filter by minimum games played
    min_games_played = st.slider("Set Minimum Games Played to Include a Season:", min_value=1, max_value=82, value=65)
    combined_df = combined_df[combined_df["g"] >= min_games_played]

    # Select on-court performance stats
    on_court_stats = [
        "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%",
        "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pts"
    ]

    # Group by injury status and calculate averages
    combined_stats = combined_df.groupby("injury status")[on_court_stats].mean()

    # Calculate total changes
    total_changes = combined_stats.loc["Post-Injury"] - combined_stats.loc["Pre-Injury"]

    # Identify the stat with the greatest change
    most_changed_stat = total_changes.abs().idxmax()
    max_total_change = total_changes[most_changed_stat]
    change_direction = "increased" if max_total_change > 0 else "decreased"

    # Display results
    st.subheader(f"Analysis for {selected_position}")
    st.dataframe(combined_stats)
    st.subheader("Total Changes (Post-Injury - Pre-Injury)")
    st.dataframe(total_changes)
    st.markdown(f"**Statistic with the most total change:** {most_changed_stat}")
    st.markdown(f"**Total Change Value:** {max_total_change:.2f} ({change_direction})")

    # Visualize results
    st.bar_chart(combined_stats.T)
    st.bar_chart(total_changes)

else:
    st.warning("Please select a position to analyze.")
