from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "lahman"

BATTING_FILE = DATA_DIR / "Batting.csv"
PEOPLE_FILE = DATA_DIR / "People.csv"


def load_lahman_batting():
    return pd.read_csv(BATTING_FILE)


def load_lahman_people():
    return pd.read_csv(PEOPLE_FILE)


def get_career_hitting_stats():
    batting = load_lahman_batting()
    people = load_lahman_people()

    career = (
        batting
        .groupby("playerID", as_index=False)
        .agg({
            "G": "sum",
            "AB": "sum",
            "R": "sum",
            "H": "sum",
            "2B": "sum",
            "3B": "sum",
            "HR": "sum",
            "RBI": "sum",
            "SB": "sum",
            "BB": "sum"
        })
    )

    # Career batting average must be calculated
    # from career H / career AB.
    career["AVG"] = career.apply(
        lambda row: row["H"] / row["AB"]
        if row["AB"] > 0
        else None,
        axis=1
    )

    people_names = people[[
        "playerID",
        "nameFirst",
        "nameLast"
    ]].copy()

    people_names["Player"] = (
        people_names["nameFirst"].fillna("")
        + " "
        + people_names["nameLast"].fillna("")
    ).str.strip()

    career = career.merge(
        people_names[["playerID", "Player"]],
        on="playerID",
        how="left"
    )

    return career