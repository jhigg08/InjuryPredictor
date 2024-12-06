# Import necessary libraries
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Streamlit App Title
st.title("NBA Injury Predictor")

# Step 1: Upload CSV Files
uploaded_files = st.file_uploader(
    "Upload Player Stats CSV Files (one or more):",
    accept_multiple_files=True,
    type=["csv"]
)

if uploaded_files:
    dataframes = []
    injury_years = {}

    # Step 2: Process Uploaded Files
    for uploaded_file in uploaded_files:
        # Read each file into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Extract player name from the file name
        player_name = uploaded_file.name.replace("_Stats.csv", "").replace("_", " ").title()

        # Allow user to input injury year for the player
        injury_year = st.number_input(
            f"Enter the injury year for {player_name}:", min_value=1900, max_value=2100, step=1
        )

        # Store the injury year
        injury_years[player_name] = injury_year

        # Add Player Name column
        df["Player"] = player_name
        dataframes.append(df)

    # Combine all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Standardize column names
    combined_df.columns = combined_df.columns.str.strip().str.lower()

    # Step 3: Clean the Data
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

    # Filter out seasons where players played fewer than the minimum games
    min_games_played = st.slider("Set Minimum Games Played to Include a Season:", min_value=1, max_value=82, value=65)
    combined_df = combined_df[combined_df["g"] >= min_games_played]

    # Step 4: Add Pre- and Post-Injury Labels
    combined_df["injury_status"] = combined_df.apply(
        lambda row: "Pre-Injury" if int(row["season"][:4]) < injury_years.get(row["player"], 9999) else "Post-Injury",
        axis=1
    )

    # Step 5: Analyze the Data
    # Select only on-court performance stats
    on_court_stats = [
        "fg", "fga", "fg%", "3p", "3pa", "3p%", "2p", "2pa", "2p%",
        "efg%", "ft", "fta", "ft%", "orb", "drb", "trb", "ast", "stl", "blk", "tov", "pts"
    ]

    # Calculate combined averages for pre- and post-injury
    combined_stats = combined_df.groupby("injury_status")[on_court_stats].mean()

    # Calculate total changes
    total_changes = combined_stats.loc["Post-Injury"] - combined_stats.loc["Pre-Injury"]

    # Identify the stat with the greatest total change
    most_changed_stat = total_changes.abs().idxmax()
    max_total_change = total_changes[most_changed_stat]

    # Determine if the change is positive or negative
    change_direction = "increased" if max_total_change > 0 else "decreased"

    # Step 6: Display Results in Streamlit
    st.subheader("Combined Pre/Post-Injury On-Court Averages")
    st.dataframe(combined_stats)

    st.subheader("Total Changes (Post-Injury - Pre-Injury)")
    st.dataframe(total_changes)

    st.markdown(f"**Statistic with the most total change:** {most_changed_stat}")
    st.markdown(f"**Total Change Value:** {max_total_change:.2f} ({change_direction})")

    # Step 7: Visualizations
    st.subheader("Visualizations")

    # Plotly bar chart for combined averages
    fig_combined = go.Figure()

    # Add Pre-Injury data
    fig_combined.add_trace(go.Bar(
        x=combined_stats.index,
        y=combined_stats["Pre-Injury"],
        name="Pre-Injury"
    ))

    # Add Post-Injury data
    fig_combined.add_trace(go.Bar(
        x=combined_stats.index,
        y=combined_stats["Post-Injury"],
        name="Post-Injury"
    ))

    # Configure layout
    fig_combined.update_layout(
        barmode="group",
        title="Combined Average On-Court Stats: Pre-Injury vs. Post-Injury",
        xaxis_title="Statistics",
        yaxis_title="Average Value",
        xaxis=dict(tickangle=45),
        legend_title="Injury Status"
    )

    # Display the grouped bar chart
    st.plotly_chart(fig_combined)

    # Plotly bar chart for total changes
    fig_changes = go.Figure()

    # Add total changes
    fig_changes.add_trace(go.Bar(
        x=total_changes.index,
        y=total_changes.values,
        name="Total Changes",
        marker_color='orange'
    ))

    # Configure layout
    fig_changes.update_layout(
        title="Total Changes in On-Court Stats: Post-Injury vs. Pre-Injury",
        xaxis_title="Statistics",
        yaxis_title="Total Change",
        xaxis=dict(tickangle=45),
        showlegend=False
    )

    # Display the total changes bar chart
    st.plotly_chart(fig_changes)

    # Option to download processed data
    csv = combined_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Processed Data",
        data=csv,
        file_name="processed_player_stats.csv",
        mime="text/csv"
    )
else:
    st.warning("Please upload at least one CSV file to proceed.")
