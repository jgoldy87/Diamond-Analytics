import pandas as pd
import plotly.express as px
import streamlit as st


HITTING_CATEGORIES = {
    "Home Runs": "HR",
    "Hits": "H",
    "RBI": "RBI",
    "Runs": "R",
    "Stolen Bases": "SB",
    "Walks": "BB",
    "Doubles": "2B",
    "Triples": "3B",
    "Batting Average": "AVG"
}


def show_all_time_leaders(get_career_hitting_stats):
    st.header("🏛️ All-Time Leaders")

    st.write(
        "Explore career hitting leaders using historical "
        "Major League Baseball data."
    )

    career_df = get_career_hitting_stats()

    if career_df.empty:
        st.warning("No historical batting data found.")
        return

    col1, col2 = st.columns(2)

    with col1:
        category_name = st.selectbox(
            "Category",
            list(HITTING_CATEGORIES.keys())
        )

    with col2:
        top_n = st.selectbox(
            "Number of Leaders",
            [10, 25, 50],
            index=0
        )

    stat_column = HITTING_CATEGORIES[category_name]

    leaders_df = career_df.copy()

    # Career AVG needs a qualification threshold so
    # players with only a handful of at-bats do not
    # dominate the leaderboard.
    if stat_column == "AVG":
        leaders_df = leaders_df[
            leaders_df["AB"] >= 3000
        ].copy()

    leaders_df = (
        leaders_df
        .dropna(subset=[stat_column])
        .sort_values(
            stat_column,
            ascending=False
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    leaders_df["Rank"] = leaders_df.index + 1

    if stat_column == "AVG":
        leaders_df["Value"] = leaders_df[
            stat_column
        ].map(lambda x: f"{x:.3f}".replace("0.", "."))

    else:
        leaders_df["Value"] = (
            leaders_df[stat_column]
            .fillna(0)
            .astype(int)
        )

    display_df = leaders_df[[
        "Rank",
        "Player",
        "Value"
    ]]

    st.subheader(
        f"Career {category_name} Leaders"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Keep the visualization readable even if the
    # user selects Top 25 or Top 50.
    chart_df = leaders_df.head(15).copy()

    fig = px.bar(
        chart_df.sort_values(
            stat_column,
            ascending=True
        ),
        x=stat_column,
        y="Player",
        orientation="h",
        title=f"Top {len(chart_df)} Career {category_name} Leaders",
        hover_data=["Rank"]
    )

    if stat_column == "AVG":
        fig.update_xaxes(
            tickformat=".3f",
            title="Batting Average"
        )
    else:
        fig.update_xaxes(
            title=category_name
        )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if stat_column == "AVG":
        st.caption(
            "Career batting-average leaderboard currently "
            "requires at least 3,000 career at-bats."
        )

    st.caption(
        "Historical statistics sourced from the Lahman Baseball Database."
    )