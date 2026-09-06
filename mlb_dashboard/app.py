import streamlit as st
from datetime import date

from api.mlb_api import (
    get_league_leaders,
    get_player_available_seasons, 
    get_standings, 
    get_schedule, 
    search_players, 
    get_player_season_stats,
    get_player_career_stats,
    get_player_team,
    get_player_game_logs
)
from pages.home import show_home_dashboard
from pages.league_leaders import show_league_leaders
from pages.scoreboard import show_daily_scoreboard
from pages.team_summary import show_team_summary
from pages.standings import show_division_standings, show_wild_card_standings
from pages.players import show_player_explorer

from api.historical import (
    get_career_hitting_stats,
    get_career_pitching_stats,
    get_single_season_hitting_stats,
    get_single_season_pitching_stats
)
from pages.historical_leaders import show_all_time_leaders

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
        "Player Explorer",
        "All-Time Leaders"
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


if page == "Home":
    show_home_dashboard(
        season,
        cached_standings,
        cached_schedule,
        cached_leaders
    )

elif page == "League Leaders":
    show_league_leaders(
        season,
        cached_leaders
    )

elif page == "Daily Scoreboard":
    show_daily_scoreboard(
        cached_schedule
    )

elif page == "Player Explorer":
    show_player_explorer(
        search_players,
        get_player_season_stats,
        get_player_career_stats,
        get_player_team,
        get_player_game_logs,
        get_player_available_seasons,
        season
    )

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

elif page == "All-Time Leaders":
    show_all_time_leaders(
        get_career_hitting_stats,
        get_career_pitching_stats,
        get_single_season_hitting_stats,
        get_single_season_pitching_stats
    )

st.caption("Data pulled from the public MLB Stats API.")