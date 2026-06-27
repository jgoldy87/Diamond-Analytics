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

def safe_get(dictionary, keys, default=None):
    current = dictionary
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default

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