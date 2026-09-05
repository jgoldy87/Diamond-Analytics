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

PITCHING_CATEGORIES = {
    "Wins": "W",
    "Strikeouts": "SO",
    "Saves": "SV",
    "Complete Games": "CG",
    "Shutouts": "SHO",
    "Games Pitched": "G",
    "Games Started": "GS",
    "Innings Pitched": "IP",
    "ERA": "ERA",
    "WHIP": "WHIP"
}

def show_all_time_leaders(
    get_career_hitting_stats,
    get_career_pitching_stats,
    get_single_season_hitting_stats,
    get_single_season_pitching_stats
):
    st.header("🏛️ All-Time Leaders")

    st.write(
        "Explore career and single-season records "
        "using historical Major League Baseball data."
    )

    record_scope = st.radio(
        "Record Type",
        ["Career Leaders", "Single-Season Records"],
        horizontal=True
    )

    leader_type = st.radio(
        "Stat Type",
        ["Hitting", "Pitching"],
        horizontal=True
    )

    era_filter = st.radio(
        "Era",
        ["All Eras", "1920–Present"],
        horizontal=True
    )

    if era_filter == "1920–Present":
        st.caption(
            "Career totals are recalculated using only statistics "
            "recorded from the 1920 season onward."
        )

    start_year = None

    if era_filter == "1920–Present":
        start_year = 1920

    # Load the appropriate dataset
    if record_scope == "Career Leaders":

        if leader_type == "Hitting":
            stats_df = get_career_hitting_stats(start_year=start_year)
            categories = HITTING_CATEGORIES

        else:
            stats_df = get_career_pitching_stats(start_year=start_year)
            categories = PITCHING_CATEGORIES

    else:

        if leader_type == "Hitting":
            stats_df = get_single_season_hitting_stats()
            categories = HITTING_CATEGORIES

        else:
            stats_df = get_single_season_pitching_stats()
            categories = PITCHING_CATEGORIES

        if start_year is not None:
            stats_df = stats_df[
                stats_df["yearID"] >= start_year
            ].copy()
    
    if stats_df.empty:
        st.warning("No historical data found.")
        return

    col1, col2 = st.columns(2)

    with col1:
        category_name = st.selectbox(
            "Category",
            list(categories.keys())
        )

    with col2:
        top_n = st.selectbox(
            "Number of Leaders",
            [10, 25, 50],
            index=0
        )

    stat_column = categories[category_name]

    leaders_df = stats_df.copy()

    # Hitting AVG qualification
    ascending = False

    if record_scope == "Career Leaders":

        if leader_type == "Hitting" and stat_column == "AVG":
            leaders_df = leaders_df[
                leaders_df["AB"] >= 3000
            ].copy()

        if leader_type == "Pitching" and stat_column in ["ERA", "WHIP"]:
            leaders_df = leaders_df[
                leaders_df["IP"] >= 1000
            ].copy()

            ascending = True

    else:

        # Single-season AVG qualification
        if leader_type == "Hitting" and stat_column == "AVG":
            leaders_df = leaders_df[
                leaders_df["AB"] >= 400
            ].copy()

        # Single-season ERA / WHIP qualification
        if leader_type == "Pitching" and stat_column in ["ERA", "WHIP"]:
            leaders_df = leaders_df[
                leaders_df["IP"] >= 150
            ].copy()

            ascending = True

    # Determine sorting direction: for ERA/WHIP lower is better
    if stat_column in ["ERA", "WHIP"]:
        ascending = True
    else:
        ascending = False

    leaders_df = (
        leaders_df
        .dropna(subset=[stat_column])
        .sort_values(stat_column, ascending=ascending)
        .head(top_n)
        .reset_index(drop=True)
    )

    leaders_df["Rank"] = leaders_df.index + 1

    # Ensure AVG formatted and integer for counting stats
    if stat_column == "AVG":
        leaders_df["Value"] = leaders_df[stat_column].map(
            lambda x: f"{x:.3f}".replace("0.", ".") if pd.notna(x) else ""
        )
    elif stat_column in ["ERA", "WHIP"]:
        leaders_df["Value"] = leaders_df[stat_column].map(
            lambda x: f"{x:.2f}" if pd.notna(x) else ""
        )
    elif stat_column == "IP":
        leaders_df["Value"] = leaders_df[stat_column].map(
            lambda x: f"{x:,.1f}" if pd.notna(x) else ""
        )
    else:
        leaders_df["Value"] = (
            leaders_df[stat_column]
            .fillna(0)
            .astype(int)
        )

    if record_scope == "Single-Season Records":

        display_df = leaders_df[[
            "Rank",
            "Player",
            "yearID",
            "Value"
        ]].copy()

        display_df = display_df.rename(
            columns={"yearID": "Season"}
        )

    else:

        display_df = leaders_df[[
            "Rank",
            "Player",
            "Value"
        ]]
    
    if record_scope == "Career Leaders":
        st.subheader(
            f"Career {category_name} Leaders"
        )
    else:
        st.subheader(
            f"Single-Season {category_name} Records"
        )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # Keep the visualization readable even if the
    # user selects Top 25 or Top 50.
    chart_df = leaders_df.head(15).copy()

    chart_df = leaders_df.head(15).copy()

    if record_scope == "Single-Season Records":
        chart_df["Label"] = (
            chart_df["Player"]
            + " ("
            + chart_df["yearID"].astype(str)
            + ")"
        )

        y_column = "Label"

    else:
        y_column = "Player"

        # For plotting, sort ascending for rate stats where lower is better
        plot_ascending = stat_column in ["ERA", "WHIP"]

    fig = px.bar(
        chart_df.sort_values(
            stat_column,
            ascending=not ascending
        ),
        x=stat_column,
        y=y_column,
        orientation="h",
        title=f"Top {len(chart_df)} {category_name}",
        hover_data=["Rank"]
    )

    if stat_column == "AVG":
        fig.update_xaxes(tickformat=".3f", title="Batting Average")
    else:
        fig.update_xaxes(title=category_name)

    st.plotly_chart(fig, use_container_width=True)

    if stat_column == "AVG":
        st.caption(
            "Career batting-average leaderboard currently requires at least 3,000 career at-bats."
        )

    st.caption("Historical statistics sourced from the Lahman Baseball Database.")