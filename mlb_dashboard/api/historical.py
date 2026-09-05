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

def get_career_pitching_stats(start_year=None):
    pitching = load_lahman_pitching()
    people = load_lahman_people()

    if start_year is not None:
        pitching = pitching[
            pitching["yearID"] >= start_year
        ].copy()

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

    career_years = (
        pitching
        .groupby("playerID")["yearID"]
        .agg(["min", "max"])
        .reset_index()
        .rename(columns={
            "min": "Career_Start",
            "max": "Career_End"
        })
    )

    career = career.merge(
        career_years,
        on="playerID",
        how="left"
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


def get_career_hitting_stats(start_year=None):
    batting = load_lahman_batting()
    people = load_lahman_people()

    if start_year is not None:
        batting = batting[
            batting["yearID"] >= start_year
        ].copy()

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

    career_years = (
        batting
        .groupby("playerID")["yearID"]
        .agg(["min", "max"])
        .reset_index()
        .rename(columns={
            "min": "Career_Start",
            "max": "Career_End"
        })
    )

    career = career.merge(
        career_years,
        on="playerID",
        how="left"
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

def get_single_season_hitting_stats():
    batting = load_lahman_batting()
    people = load_lahman_people()

    # A player can have multiple rows in one season if traded,
    # so aggregate by player + season first.
    season_stats = (
        batting
        .groupby(["playerID", "yearID"], as_index=False)
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

    season_stats["AVG"] = season_stats.apply(
        lambda row: (
            row["H"] / row["AB"]
            if row["AB"] > 0
            else None
        ),
        axis=1
    )

    people_names = people[
        ["playerID", "nameFirst", "nameLast"]
    ].copy()

    people_names["Player"] = (
        people_names["nameFirst"].fillna("")
        + " "
        + people_names["nameLast"].fillna("")
    ).str.strip()

    season_stats = season_stats.merge(
        people_names[["playerID", "Player"]],
        on="playerID",
        how="left"
    )

    return season_stats


def get_single_season_pitching_stats():
    pitching = load_lahman_pitching()
    people = load_lahman_people()

    season_stats = (
        pitching
        .groupby(["playerID", "yearID"], as_index=False)
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

    season_stats["IP"] = season_stats["IPouts"] / 3

    season_stats["ERA"] = season_stats.apply(
        lambda row: (
            row["ER"] * 9 / row["IP"]
            if row["IP"] > 0
            else None
        ),
        axis=1
    )

    season_stats["WHIP"] = season_stats.apply(
        lambda row: (
            (row["BB"] + row["H"]) / row["IP"]
            if row["IP"] > 0
            else None
        ),
        axis=1
    )

    people_names = people[
        ["playerID", "nameFirst", "nameLast"]
    ].copy()

    people_names["Player"] = (
        people_names["nameFirst"].fillna("")
        + " "
        + people_names["nameLast"].fillna("")
    ).str.strip()

    season_stats = season_stats.merge(
        people_names[["playerID", "Player"]],
        on="playerID",
        how="left"
    )

    return season_stats