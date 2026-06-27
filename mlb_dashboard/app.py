import pandas as pd
import streamlit as st
import plotly.express as px

from mlb_api import get_league_leaders, get_standings, get_schedule
from standings import show_division_standings, show_wild_card_standings

st.set_page_config(page_title="MLB Stats Dashboard", layout="wide")

st.title("⚾ Diamond Analytics")

season = st.sidebar.selectbox("Season", list(range(2026, 2015, -1)))

page = st.sidebar.radio(
    "Dashboard Section",
    [
        "League Leaders",
        "Division Standings",
        "Wild Card Standings",
        "Daily Scoreboard",
        "Team Summary"
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

if page == "League Leaders":
    show_league_leaders()

elif page == "Daily Scoreboard":
    show_daily_scoreboard()

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