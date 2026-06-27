import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="MLB Stats Dashboard", layout="wide")

BASE_URL = "https://statsapi.mlb.com/api/v1"

LEAGUES = {
    "American League": 103,
    "National League": 104
}

DIVISIONS = {
    200: "AL West",
    201: "AL East",
    202: "AL Central",
    203: "NL West",
    204: "NL East",
    205: "NL Central"
}


@st.cache_data(ttl=1800)
def get_league_leaders(season, stat, group, limit=10):
    url = f"{BASE_URL}/stats/leaders"
    params = {
        "leaderCategories": stat,
        "statGroup": group,
        "season": season,
        "limit": limit,
        "sportId": 1
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    leaders = data["leagueLeaders"][0]["leaders"]

    rows = []
    for player in leaders:
        rows.append({
            "Rank": player.get("rank"),
            "Player": player["person"]["fullName"],
            "Team": player.get("team", {}).get("name", "N/A"),
            "Value": player["value"]
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=1800)
def get_standings(season):
    url = f"{BASE_URL}/standings"
    params = {
        "leagueId": "103,104",
        "season": season,
        "standingsTypes": "regularSeason",
        "sportId": 1
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    rows = []

    for record_group in data["records"]:
        division_id = record_group["division"]["id"]
        division_name = DIVISIONS.get(
            division_id,
            record_group.get("division", {}).get("name", "Unknown Division")
    )

        for team_record in record_group["teamRecords"]:
            rows.append({
                "Team": team_record["team"]["name"],
                "League": team_record["league"]["name"],
                "Division": division_name,
                "Wins": team_record["wins"],
                "Losses": team_record["losses"],
                "Pct": float(team_record["winningPercentage"]),
                "GB": team_record.get("gamesBack", "-"),
                "Division Rank": int(team_record.get("divisionRank", 99)),
                "League Rank": int(team_record.get("leagueRank", 99)),
                "Wild Card Rank": int(team_record.get("wildCardRank", 99)),
                "Wild Card GB": team_record.get("wildCardGamesBack", "-"),
                "Run Differential": team_record.get("runDifferential", 0),
                "Streak": team_record.get("streak", {}).get("streakCode", "")
            })

    return pd.DataFrame(rows)


def show_league_leaders(season):
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

    df = get_league_leaders(season, stat, group)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(df, use_container_width=True)

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


def show_division_standings(standings_df):
    st.header("📊 Current Division Standings")

    league_filter = st.selectbox(
        "League",
        ["All MLB", "American League", "National League"]
    )

    df = standings_df.copy()

    if league_filter != "All MLB":
        df = df[df["League"] == league_filter]

    for division in sorted(df["Division"].unique()):
        st.subheader(division)

        div_df = (
            df[df["Division"] == division]
            .sort_values("Division Rank")
            [[
                "Division Rank",
                "Team",
                "Wins",
                "Losses",
                "Pct",
                "GB",
                "Run Differential",
                "Streak"
            ]]
        )

        st.dataframe(div_df, use_container_width=True, hide_index=True)

        chart_df = div_df.copy()
        fig = px.bar(
            chart_df.sort_values("Wins", ascending=True),
            x="Wins",
            y="Team",
            orientation="h",
            title=f"{division} Wins"
        )

        st.plotly_chart(fig, use_container_width=True)


def show_wild_card_standings(standings_df):
    st.header("🔥 Wild Card Standings")

    for league in ["American League", "National League"]:
        st.subheader(league)

        league_df = standings_df[standings_df["League"] == league].copy()

        # Division leaders are not part of the Wild Card race
        wild_card_df = league_df[league_df["Division Rank"] != 1].copy()

        wild_card_df = wild_card_df.sort_values("Wild Card Rank")

        display_df = wild_card_df[[
            "Wild Card Rank",
            "Team",
            "Wins",
            "Losses",
            "Pct",
            "Wild Card GB",
            "Run Differential",
            "Streak"
        ]]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        fig = px.bar(
            display_df.sort_values("Wins", ascending=True),
            x="Wins",
            y="Team",
            orientation="h",
            title=f"{league} Wild Card Race"
        )

        st.plotly_chart(fig, use_container_width=True)


st.title("⚾ MLB Statistics Dashboard")

season = st.sidebar.selectbox("Season", list(range(2026, 2015, -1)))

page = st.sidebar.radio(
    "Dashboard Section",
    [
        "League Leaders",
        "Division Standings",
        "Wild Card Standings"
    ]
)

if page == "League Leaders":
    show_league_leaders(season)

else:
    standings_df = get_standings(season)

    if page == "Division Standings":
        show_division_standings(standings_df)

    elif page == "Wild Card Standings":
        show_wild_card_standings(standings_df)

st.caption("Data pulled from the public MLB Stats API.")