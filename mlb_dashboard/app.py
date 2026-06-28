import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date

from api.mlb_api import (
    get_league_leaders, 
    get_standings, 
    get_schedule, 
    search_players, 
    get_player_season_stats,
    get_player_team
)
from pages.standings import show_division_standings, show_wild_card_standings
from pages.players import show_player_explorer

st.set_page_config(page_title="MLB Stats Dashboard", layout="wide")

st.sidebar.title("⚾ Diamond Analytics")

season = st.sidebar.selectbox("Season", list(range(2026, 2015, -1)))

page = st.sidebar.radio(
    "Dashboard Section",
    [
        "Home",
        "League Leaders",
        "Division Standings",
        "Wild Card Standings",
        "Daily Scoreboard",
        "Team Summary",
        "Player Explorer"
    ]
)

@st.cache_data(ttl=1800)
def cached_standings(selected_season):
    return get_standings(selected_season)

@st.cache_data(ttl=1800)
def cached_leaders(selected_season, stat, group):
    return get_league_leaders(selected_season, stat, group)

@st.cache_data(ttl=900)
def cached_schedule(selected_date):
    return get_schedule(selected_date)

def show_league_leaders():
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

    category = st.selectbox("Stat Category", list(category_map.keys()))
    stat, group = category_map[category]

    df = cached_leaders(season, stat, group)

    if df.empty:
        st.warning("No league leader data found.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col2:
        chart_df = df.copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")

        fig = px.bar(
            chart_df.sort_values("Value", ascending=True),
            x="Value",
            y="Player",
            orientation="h",
            title=f"{season} MLB Leaders: {category}",
            hover_data=["Team", "Rank"]
        )

        st.plotly_chart(fig, use_container_width=True)

def show_daily_scoreboard():
    st.header("📅 Daily Scoreboard")

    selected_date = st.date_input("Select Date")

    df = cached_schedule(selected_date.strftime("%Y-%m-%d"))

    if df.empty:
        st.warning("No games found for this date.")
        return

    display_df = df.copy()

    display_df["Away Score"] = display_df["Away Score"].fillna("")
    display_df["Home Score"] = display_df["Home Score"].fillna("")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    scored_games = df.dropna(subset=["Away Score", "Home Score"]).copy()

    if scored_games.empty:
        st.info("No scored games yet for this date.")
        return

    scored_games["Away Score"] = scored_games["Away Score"].astype(int)
    scored_games["Home Score"] = scored_games["Home Score"].astype(int)

    chart_df = scored_games.melt(
        id_vars=["Game"],
        value_vars=["Away Score", "Home Score"],
        var_name="Team Type",
        value_name="Runs"
    )

    fig = px.bar(
        chart_df,
        x="Game",
        y="Runs",
        color="Team Type",
        barmode="group",
        title="Runs by Game"
    )

    st.plotly_chart(fig, use_container_width=True)


def show_team_summary(standings_df):
    st.header("🏟️ Team Summary")

    team = st.selectbox(
        "Select Team",
        sorted(standings_df["Team"].unique())
    )

    team_row = standings_df[standings_df["Team"] == team].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Record", f"{team_row['Wins']}-{team_row['Losses']}")
    col2.metric("Win %", f"{team_row['Pct']:.3f}")
    col3.metric("Division", team_row["Division"])
    col4.metric("Run Differential", team_row["Run Differential"])

    st.subheader("Standings Context")

    context_df = standings_df[
        standings_df["Division"] == team_row["Division"]
    ].sort_values("Division Rank")

    st.dataframe(
        context_df[[
            "Division Rank",
            "Team",
            "Wins",
            "Losses",
            "Pct",
            "GB",
            "Run Differential",
            "Streak"
        ]],
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        context_df.sort_values("Wins", ascending=True),
        x="Wins",
        y="Team",
        orientation="h",
        title=f"{team_row['Division']} Wins Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

def show_home_dashboard():
    st.markdown(
        """
        # ⚾ Diamond Analytics

        **Interactive MLB statistics and baseball analytics powered by Python.**

        Explore live standings, Wild Card races, league leaders, daily games, team summaries, and player statistics through an interactive web dashboard.
        """
    )

    st.divider()

    st.subheader("🚀 What You Can Explore")

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown(
            """
            ### 📊 Standings
            View current division standings and Wild Card races across MLB.
            """
        )

    with feature_col2:
        st.markdown(
            """
            ### 🏆 League Leaders
            Track top hitters and pitchers in key statistical categories.
            """
        )

    with feature_col3:
        st.markdown(
            """
            ### 👤 Player Explorer
            Search MLB players and view season stats, team info, and player details.
            """
        )

    feature_col4, feature_col5, feature_col6 = st.columns(3)

    with feature_col4:
        st.markdown(
            """
            ### 📅 Daily Scoreboard
            See today’s MLB matchups, scores, statuses, and venues.
            """
        )

    with feature_col5:
        st.markdown(
            """
            ### 🏟️ Team Explorer
            Review team records, division context, recent games, and performance.
            """
        )

    with feature_col6:
        st.markdown(
            """
            ### 📈 Analytics Roadmap
            Future updates will include career stats, player trends, historical data, and advanced metrics.
            """
        )

    st.divider()

    st.subheader("⚡ MLB At a Glance")

    standings_df = cached_standings(season)

    if standings_df.empty:
        st.warning("No standings data found.")
        return

    col1, col2, col3 = st.columns(3)

    best_team = standings_df.sort_values("Pct", ascending=False).iloc[0]
    most_wins = standings_df.sort_values("Wins", ascending=False).iloc[0]
    best_run_diff = standings_df.sort_values("Run Differential", ascending=False).iloc[0]

    col1.metric("Best Win %", best_team["Team"], f"{best_team['Pct']:.3f}")
    col2.metric("Most Wins", most_wins["Team"], int(most_wins["Wins"]))
    col3.metric("Best Run Differential", best_run_diff["Team"], int(best_run_diff["Run Differential"]))

    st.divider()

    st.subheader("📅 Today's Games")

    today = date.today().strftime("%Y-%m-%d")
    today_games = cached_schedule(today)

    if today_games.empty:
        st.info("No MLB games scheduled for today.")
    else:
        games_display = today_games[[
            "Game",
            "Away Score",
            "Home Score",
            "Status",
            "Venue"
        ]].copy()

        games_display["Away Score"] = games_display["Away Score"].fillna("")
        games_display["Home Score"] = games_display["Home Score"].fillna("")

        st.dataframe(
            games_display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("🏆 Featured League Leaders")

    leader_col1, leader_col2, leader_col3 = st.columns(3)

    hr_df = cached_leaders(season, "homeRuns", "hitting")
    avg_df = cached_leaders(season, "battingAverage", "hitting")
    era_df = cached_leaders(season, "earnedRunAverage", "pitching")

    with leader_col1:
        st.markdown("### Home Runs")
        if not hr_df.empty:
            leader = hr_df.iloc[0]
            st.metric(leader["Player"], leader["Value"])
            st.caption(leader["Team"])
        else:
            st.info("No data found.")

    with leader_col2:
        st.markdown("### Batting Average")
        if not avg_df.empty:
            leader = avg_df.iloc[0]
            st.metric(leader["Player"], leader["Value"])
            st.caption(leader["Team"])
        else:
            st.info("No data found.")

    with leader_col3:
        st.markdown("### ERA")
        if not era_df.empty:
            leader = era_df.iloc[0]
            st.metric(leader["Player"], leader["Value"])
            st.caption(leader["Team"])
        else:
            st.info("No data found.")

    st.divider()

    st.subheader("🔥 Wild Card Snapshot")

    for league in ["American League", "National League"]:
        st.markdown(f"**{league}**")

        league_df = standings_df[standings_df["League"] == league].copy()

        division_leader_teams = (
            league_df
            .sort_values(["Division", "Wins", "Pct"], ascending=[True, False, False])
            .groupby("Division")
            .head(1)["Team"]
            .tolist()
        )

        wc_df = (
            league_df[~league_df["Team"].isin(division_leader_teams)]
            .sort_values(["Wins", "Pct", "Run Differential"], ascending=False)
            .head(3)
            [["Team", "Wins", "Losses", "Pct", "Run Differential"]]
        )

        st.dataframe(wc_df, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown(
        """
        ### About This Project

        Diamond Analytics is a personal baseball analytics project built with **Python**, **Streamlit**, **Pandas**, **Plotly**, and the **MLB Stats API**.

        The goal is to create an accessible, interactive MLB dashboard while continuing to develop practical skills in data analysis, API integration, visualization, and software development.
        """
    )

if page == "Home":
    show_home_dashboard()

elif page == "League Leaders":
    show_league_leaders()

elif page == "Daily Scoreboard":
    show_daily_scoreboard()

elif page == "Player Explorer":
    show_player_explorer(search_players, get_player_season_stats, get_player_team, season)

elif page == "Division Standings":
    standings_df = cached_standings(season)

    if standings_df.empty:
        st.warning("No standings data found.")
    else:
        show_division_standings(standings_df)

elif page == "Wild Card Standings":
    standings_df = cached_standings(season)

    if standings_df.empty:
        st.warning("No standings data found.")
    else:
        show_wild_card_standings(standings_df)

elif page == "Team Summary":
    standings_df = cached_standings(season)

    if standings_df.empty:
        st.warning("No standings data found.")
    else:
        show_team_summary(standings_df)

st.caption("Data pulled from the public MLB Stats API.")