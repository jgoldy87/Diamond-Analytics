from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "lahman"

BATTING_FILE = DATA_DIR / "Batting.csv"
PEOPLE_FILE = DATA_DIR / "People.csv"
PITCHING_FILE = DATA_DIR / "Pitching.csv"


def load_lahman_batting():
    return pd.read_csv(BATTING_FILE)


def load_lahman_people():
    return pd.read_csv(PEOPLE_FILE)

def load_lahman_pitching():
    return pd.read_csv(PITCHING_FILE)

def get_career_pitching_stats():
    pitching = load_lahman_pitching()
    people = load_lahman_people()

    career = (
        pitching
        .groupby("playerID", as_index=False)
        .agg({
            "G": "sum",
            "GS": "sum",
            "W": "sum",
            "L": "sum",
            "SV": "sum",
            "SO": "sum",
            "BB": "sum",
            "H": "sum",
            "HR": "sum",
            "ER": "sum",
            "IPouts": "sum",
            "CG": "sum",
            "SHO": "sum"
        })
    )

    # Convert outs into innings pitched
    career["IP"] = career["IPouts"] / 3

    # Career ERA
    career["ERA"] = career.apply(
        lambda row: (
            row["ER"] * 9 / row["IP"]
            if row["IP"] > 0
            else None
        ),
        axis=1
    )

    # Career WHIP
    career["WHIP"] = career.apply(
        lambda row: (
            (row["BB"] + row["H"]) / row["IP"]
            if row["IP"] > 0
            else None
        ),
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