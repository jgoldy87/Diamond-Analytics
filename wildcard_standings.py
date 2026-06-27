import requests

BASE_URL = "https://statsapi.mlb.com/api/v1"


def get_standings(season=None):
    params = {
        "leagueId": "103,104",
        "standingsTypes": "regularSeason",
        "hydrate": "team,division,league"
    }

    if season:
        params["season"] = season

    response = requests.get(f"{BASE_URL}/standings", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_teams(data):
    teams = []

    for record in data.get("records", []):
        league = record.get("league", {}).get("name", "")
        division = record.get("division", {}).get("name", "")

        for team_record in record.get("teamRecords", []):
            team = team_record.get("team", {})

            teams.append({
                "league": league,
                "division": division,
                "team": team.get("name"),
                "wins": team_record.get("wins", 0),
                "losses": team_record.get("losses", 0),
                "pct": float(team_record.get("winningPercentage", 0)),
                "wc_gb": team_record.get("wildCardGamesBack", "-"),
                "div_gb": team_record.get("divisionGamesBack", "-"),
                "streak": team_record.get("streak", {}).get("streakCode", "")
            })

    return teams


def print_wild_card(teams, league_name):
    league_teams = [t for t in teams if league_name in t["league"]]

    # Sort by winning percentage, then wins
    league_teams.sort(key=lambda x: (x["pct"], x["wins"]), reverse=True)

    print(f"\n{league_name.upper()} WILD CARD STANDINGS")
    print("-" * 75)
    print(f"{'Team':30} {'W':>4} {'L':>4} {'Pct':>7} {'WC GB':>8} {'Streak':>8}")
    print("-" * 75)

    for team in league_teams:
        print(
            f"{team['team']:30} "
            f"{team['wins']:>4} "
            f"{team['losses']:>4} "
            f"{team['pct']:>7.3f} "
            f"{team['wc_gb']:>8} "
            f"{team['streak']:>8}"
        )


def main():
    data = get_standings()
    teams = parse_teams(data)

    if not teams:
        print("No standings data returned.")
        print("Raw keys:", data.keys())
        return

    print_wild_card(teams, "American League")
    print_wild_card(teams, "National League")


if __name__ == "__main__":
    main()