
from plotly import data
import requests
import pandas as pd
from datetime import date

BASE_URL = "https://statsapi.mlb.com/api/v1"

DIVISIONS = {
    200: "AL West",
    201: "AL East",
    202: "AL Central",
    203: "NL West",
    204: "NL East",
    205: "NL Central",
}

def safe_get(data, keys, default=None):
    current = data

    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and isinstance(key, int):
            if 0 <= key < len(current):
                current = current[key]
            else:
                return default
        else:
            return default

        if current is None:
            return default

    return current

def get_json(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def get_league_leaders(season, stat, group, limit=10):
    data = get_json("stats/leaders", {
        "leaderCategories": stat,
        "statGroup": group,
        "season": season,
        "limit": limit,
        "sportId": 1
    })

    leaders = safe_get(data, ["leagueLeaders"], [])
    if not leaders:
        return pd.DataFrame()

    rows = []
    for player in leaders[0].get("leaders", []):
        rows.append({
            "Rank": player.get("rank"),
            "Player": safe_get(player, ["person", "fullName"], "Unknown"),
            "Team": safe_get(player, ["team", "name"], "N/A"),
            "Value": player.get("value")
        })

    return pd.DataFrame(rows)

def get_standings(season):
    data = get_json("standings", {
        "leagueId": "103,104",
        "season": season,
        "standingsTypes": "regularSeason",
        "sportId": 1
    })

    rows = []

    for group in data.get("records", []):
        division_id = safe_get(group, ["division", "id"])
        division = DIVISIONS.get(division_id, f"Division {division_id}")

        if division.startswith("AL"):
            league = "American League"
        elif division.startswith("NL"):
            league = "National League"
        else:
            league = "Unknown League"

        for team in group.get("teamRecords", []):
            rows.append({
                "Team": safe_get(team, ["team", "name"], "Unknown"),
                "League": league,
                "Division": division,
                "Wins": team.get("wins", 0),
                "Losses": team.get("losses", 0),
                "Pct": float(team.get("winningPercentage", 0)),
                "GB": team.get("gamesBack", "-"),
                "Division Rank": int(team.get("divisionRank", 99)),
                "League Rank": int(team.get("leagueRank", 99)),
                "Wild Card Rank": int(team.get("wildCardRank", 99)),
                "Wild Card GB": team.get("wildCardGamesBack", "-"),
                "Run Differential": team.get("runDifferential", 0),
                "Streak": safe_get(team, ["streak", "streakCode"], "")
            })

    return pd.DataFrame(rows)

def get_schedule(selected_date):
    data = get_json("schedule", {
        "sportId": 1,
        "date": selected_date
    })

    rows = []

    for game_date in data.get("dates", []):
        for game in game_date.get("games", []):
            away = safe_get(game, ["teams", "away", "team", "name"], "Unknown")
            home = safe_get(game, ["teams", "home", "team", "name"], "Unknown")

            away_score = safe_get(game, ["teams", "away", "score"], None)
            home_score = safe_get(game, ["teams", "home", "score"], None)

            rows.append({
                "Game": f"{away} @ {home}",
                "Away Team": away,
                "Home Team": home,
                "Away Score": away_score,
                "Home Score": home_score,
                "Status": safe_get(game, ["status", "detailedState"], "Unknown"),
                "Start Time": game.get("gameDate", ""),
                "Venue": safe_get(game, ["venue", "name"], "Unknown")
            })

    return pd.DataFrame(rows)

def search_players(player_name, season=2026):
    data = get_json("sports/1/players", {
        "season": season
    })

    rows = []

    search_text = player_name.lower()

    for player in data.get("people", []):
        full_name = player.get("fullName", "")

        if search_text in full_name.lower():
            rows.append({
                "Player ID": player.get("id"),
                "Name": full_name,
                "First Name": player.get("firstName"),
                "Last Name": player.get("lastName"),
                "Primary Position": safe_get(player, ["primaryPosition", "abbreviation"], "N/A"),
                "Current Team": safe_get(player, ["currentTeam", "name"], "N/A"),
                "Birth Date": player.get("birthDate"),
                "Height": player.get("height"),
                "Weight": player.get("weight"),
                "Bats": safe_get(player, ["batSide", "code"], "N/A"),
                "Throws": safe_get(player, ["pitchHand", "code"], "N/A")
            })

    return pd.DataFrame(rows)


def get_player_season_stats(player_id, season, group):
    data = get_json(f"people/{player_id}", {
        "hydrate": f"stats(type=season,group={group},season={season})"
    })

    split = safe_get(
        data,
        ["people", 0, "stats", 0, "splits", 0],
        {}
    )

    if not split:
        return pd.DataFrame(), "N/A"

    team_name = safe_get(split, ["team", "name"], "N/A")
    stat = split.get("stat", {})

    if not stat:
        return pd.DataFrame(), team_name

    rows = []

    for key, value in stat.items():
        rows.append({
            "Stat": key,
            "Value": value
        })

    return pd.DataFrame(rows), team_name

def get_player_team(player_id, season):
    # First try current team from player profile
    data = get_json(f"people/{player_id}", {
        "hydrate": "currentTeam"
    })

    team_name = safe_get(data, ["people", 0, "currentTeam", "name"], "N/A")

    if team_name != "N/A":
        return team_name

    # If currentTeam is missing, try hitting stats
    for group in ["hitting", "pitching"]:
        data = get_json(f"people/{player_id}", {
            "hydrate": f"stats(type=season,group={group},season={season})"
        })

        team_name = safe_get(
            data,
            ["people", 0, "stats", 0, "splits", 0, "team", "name"],
            "N/A"
        )

        if team_name != "N/A":
            return team_name

    return "N/A"

def get_player_game_logs(player_id, season, group):
    data = get_json(f"people/{player_id}", {
        "hydrate": f"stats(type=gameLog,group={group},season={season})"
    })

    splits = safe_get(
        data,
        ["people", 0, "stats", 0, "splits"],
        []
    )

    if not splits:
        return pd.DataFrame()

    rows = []

    for game in splits:
        stat = game.get("stat", {})

        rows.append({
            "Date": game.get("date"),
            "Opponent": safe_get(game, ["opponent", "name"], "N/A"),
            "Team": safe_get(game, ["team", "name"], "N/A"),
            "Game PK": safe_get(game, ["game", "gamePk"], None),

            # Hitting
            "AB": stat.get("atBats"),
            "H": stat.get("hits"),
            "R": stat.get("runs"),
            "HR": stat.get("homeRuns"),
            "RBI": stat.get("rbi"),
            "BB": stat.get("baseOnBalls"),
            "SO": stat.get("strikeOuts"),

            # Pitching
            "IP": stat.get("inningsPitched"),
            "ER": stat.get("earnedRuns"),
            "P_SO": stat.get("strikeOuts"),
            "P_BB": stat.get("baseOnBalls"),
            "P_H": stat.get("hits"),
            "P_HR": stat.get("homeRuns"),
        })

    return pd.DataFrame(rows)