import plotly.express as px
import streamlit as st


def show_team_summary(standings_df):
    st.header("🏟️ Team Summary")

    team = st.selectbox(
        "Select Team",
        sorted(standings_df["Team"].unique())
    )

    team_row = standings_df[
        standings_df["Team"] == team
    ].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Record",
        f"{team_row['Wins']}-{team_row['Losses']}"
    )

    col2.metric(
        "Win %",
        f"{team_row['Pct']:.3f}"
    )

    col3.metric(
        "Division",
        team_row["Division"]
    )

    col4.metric(
        "Run Differential",
        team_row["Run Differential"]
    )

    st.subheader("Standings Context")

    context_df = standings_df[
        standings_df["Division"] == team_row["Division"]
    ].sort_values("Division Rank")

    st.dataframe(
        context_df[
            [
                "Division Rank",
                "Team",
                "Wins",
                "Losses",
                "Pct",
                "GB",
                "Run Differential",
                "Streak"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        context_df.sort_values(
            "Wins",
            ascending=True
        ),
        x="Wins",
        y="Team",
        orientation="h",
        title=f"{team_row['Division']} Wins Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )