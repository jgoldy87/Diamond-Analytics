import pandas as pd
import plotly.express as px
import streamlit as st


def show_league_leaders(
    season,
    cached_leaders
):
    st.header("🏆 League Leaders")

    category_map = {
        "Home Runs": ("homeRuns", "hitting"),
        "Batting Average": ("battingAverage", "hitting"),
        "RBI": ("runsBattedIn", "hitting"),
        "Stolen Bases": ("stolenBases", "hitting"),
        "ERA": ("earnedRunAverage", "pitching"),
        "Strikeouts": ("strikeouts", "pitching"),
        "Wins": ("wins", "pitching"),
        "WHIP": ("walksAndHitsPerInningPitched", "pitching")
    }

    category = st.selectbox(
        "Stat Category",
        list(category_map.keys())
    )

    stat, group = category_map[category]

    df = cached_leaders(
        season,
        stat,
        group
    )

    if df.empty:
        st.warning("No league leader data found.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    with col2:
        chart_df = df.copy()

        chart_df["Value"] = pd.to_numeric(
            chart_df["Value"],
            errors="coerce"
        )

        fig = px.bar(
            chart_df.sort_values(
                "Value",
                ascending=True
            ),
            x="Value",
            y="Player",
            orientation="h",
            title=f"{season} MLB Leaders: {category}",
            hover_data=["Team", "Rank"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )