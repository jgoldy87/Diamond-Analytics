from datetime import date

import streamlit as st


def show_home_dashboard(
    season,
    cached_standings,
    cached_schedule,
    cached_leaders
):
    st.markdown(
        """
        # ⚾ Diamond Analytics

        **Interactive MLB statistics and baseball analytics powered by Python.**

        Explore live standings, Wild Card races, league leaders, daily games,
        team summaries, and player statistics through an interactive web dashboard.
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
            Search MLB players and view season stats, career stats,
            historical seasons, trends, and player details.
            """
        )

    feature_col4, feature_col5, feature_col6 = st.columns(3)

    with feature_col4:
        st.markdown(
            """
            ### 📅 Daily Scoreboard
            See today's MLB matchups, scores, statuses, and venues.
            """
        )

    with feature_col5:
        st.markdown(
            """
            ### 🏟️ Team Explorer
            Review team records, division context, and performance.
            """
        )

    with feature_col6:
        st.markdown(
            """
            ### 🏛️ Historical Leaders
            Explore career and single-season records across MLB history.
            """
        )

    st.divider()

    st.subheader("⚡ MLB At a Glance")

    standings_df = cached_standings(season)

    if standings_df.empty:
        st.warning("No standings data found.")
        return

    col1, col2, col3 = st.columns(3)

    best_team = standings_df.sort_values(
        "Pct",
        ascending=False
    ).iloc[0]

    most_wins = standings_df.sort_values(
        "Wins",
        ascending=False
    ).iloc[0]

    best_run_diff = standings_df.sort_values(
        "Run Differential",
        ascending=False
    ).iloc[0]

    col1.metric(
        "Best Win %",
        best_team["Team"],
        f"{best_team['Pct']:.3f}"
    )

    col2.metric(
        "Most Wins",
        most_wins["Team"],
        int(most_wins["Wins"])
    )

    col3.metric(
        "Best Run Differential",
        best_run_diff["Team"],
        int(best_run_diff["Run Differential"])
    )

    st.divider()

    st.subheader("📅 Today's Games")

    today = date.today().strftime("%Y-%m-%d")
    today_games = cached_schedule(today)

    if today_games.empty:
        st.info("No MLB games scheduled for today.")
    else:
        games_display = today_games[
            [
                "Game",
                "Away Score",
                "Home Score",
                "Status",
                "Venue"
            ]
        ].copy()

        games_display["Away Score"] = (
            games_display["Away Score"].fillna("")
        )

        games_display["Home Score"] = (
            games_display["Home Score"].fillna("")
        )

        st.dataframe(
            games_display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("🏆 Featured League Leaders")

    leader_col1, leader_col2, leader_col3 = st.columns(3)

    hr_df = cached_leaders(
        season,
        "homeRuns",
        "hitting"
    )

    avg_df = cached_leaders(
        season,
        "battingAverage",
        "hitting"
    )

    era_df = cached_leaders(
        season,
        "earnedRunAverage",
        "pitching"
    )

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

    for league in [
        "American League",
        "National League"
    ]:
        st.markdown(f"**{league}**")

        league_df = standings_df[
            standings_df["League"] == league
        ].copy()

        division_leader_teams = (
            league_df
            .sort_values(
                ["Division", "Wins", "Pct"],
                ascending=[True, False, False]
            )
            .groupby("Division")
            .head(1)["Team"]
            .tolist()
        )

        wc_df = (
            league_df[
                ~league_df["Team"].isin(
                    division_leader_teams
                )
            ]
            .sort_values(
                [
                    "Wins",
                    "Pct",
                    "Run Differential"
                ],
                ascending=False
            )
            .head(3)
            [
                [
                    "Team",
                    "Wins",
                    "Losses",
                    "Pct",
                    "Run Differential"
                ]
            ]
        )

        st.dataframe(
            wc_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.markdown(
        """
        ### About This Project

        Diamond Analytics is a personal baseball analytics project built with
        **Python**, **Streamlit**, **Pandas**, **Plotly**, and the
        **MLB Stats API**.

        The goal is to create an accessible, interactive MLB dashboard while
        continuing to develop practical skills in data analysis, API integration,
        visualization, and software development.
        """
    )