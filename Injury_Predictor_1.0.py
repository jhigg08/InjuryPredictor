# Import necessary libraries
import pandas as pd
import streamlit as st
import altair as alt  # New import for Altair

# Streamlit App Title
st.title("NBA Injury Predictor by Position")
st.image("images/nbapic4.jpg", caption="Amar'e Stoudemire - Knicks", use_container_width=True)

# Define available players and their corresponding CSVs
# (Your existing code for positions and player data remains unchanged)

# Step 1: Select Position
selected_position = st.selectbox("Select Position:", list(positions.keys()))

if selected_position:
    # (Your existing code for loading and processing data remains unchanged)

    # Replace the Visualizations section here
    combined_stats.reset_index(inplace=True)
    melted_stats = combined_stats.melt(id_vars=["injury_status"], var_name="Stat", value_name="Value")

    # Create a side-by-side bar chart
    bar_chart = alt.Chart(melted_stats).mark_bar().encode(
        x=alt.X("Stat:N", title="Statistic"),
        y=alt.Y("Value:Q", title="Average Value"),
        color="injury_status:N",  # Differentiates Pre-Injury and Post-Injury
        tooltip=["injury_status:N", "Stat:N", "Value:Q"]
    ).properties(
        width=600,
        height=400
    )

    st.subheader("Side-by-Side Bar Chart - Combined Stats")
    st.altair_chart(bar_chart, use_container_width=True)

    # Total changes visualized as a bar chart
    total_changes_df = total_changes.reset_index()
    total_changes_df.columns = ["Stat", "Change"]

    total_changes_chart = alt.Chart(total_changes_df).mark_bar().encode(
        x=alt.X("Stat:N", title="Statistic"),
        y=alt.Y("Change:Q", title="Change in Value"),
        color=alt.condition(
            alt.datum.Change > 0,  # Highlight positive and negative changes
            alt.value("green"),  # Positive
            alt.value("red")     # Negative
        ),
        tooltip=["Stat:N", "Change:Q"]
    ).properties(
        width=600,
        height=400
    )

    st.subheader("Total Changes (Post-Injury - Pre-Injury)")
    st.altair_chart(total_changes_chart, use_container_width=True)

# Add bottom image
st.image("images/nbapic1.jpg", caption="Kobe Bryant - Lakers", use_container_width=True)
