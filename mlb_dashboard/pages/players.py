import pandas as pd
import streamlit as st
import plotly.express as px


def get_player_headshot_url(player_id):
    return f"https://img.mlbstatic.com/mlb-photos/image/upload/w_240,q_100/v1/people/{player_id}/headshot/67/current"

def get_stat_value(stats_df, stat_name, default="N/A"):
    if stats_df.empty:
        return default

    match = stats_df[stats_df["Stat"] == stat_name]

    if match.empty:
        return default

    return match.iloc[0]["Value"]


def show_featured_stat_cards(stats_df, stat_group):
    st.subheader("⭐ Featured Stats")

    if stat_group == "hitting":
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

        row1_col1.metric("Games", get_stat_value(stats_df, "gamesPlayed"))
        row1_col2.metric("AVG", get_stat_value(stats_df, "avg"))
        row1_col3.metric("HR", get_stat_value(stats_df, "homeRuns"))
        row1_col4.metric("RBI", get_stat_value(stats_df, "rbi"))

        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

        row2_col1.metric("OBP", get_stat_value(stats_df, "obp"))
        row2_col2.metric("SLG", get_stat_value(stats_df, "slg"))
        row2_col3.metric("OPS", get_stat_value(stats_df, "ops"))
        row2_col4.metric("SB", get_stat_value(stats_df, "stolenBases"))

    elif stat_group == "pitching":
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

        row1_col1.metric("Games", get_stat_value(stats_df, "gamesPlayed"))
        row1_col2.metric("ERA", get_stat_value(stats_df, "era"))
        row1_col3.metric("WHIP", get_stat_value(stats_df, "whip"))
        row1_col4.metric("SO", get_stat_value(stats_df, "strikeOuts"))

        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

        row2_col1.metric("Wins", get_stat_value(stats_df, "wins"))
        row2_col2.metric("Losses", get_stat_value(stats_df, "losses"))
        row2_col3.metric("Saves", get_stat_value(stats_df, "saves"))
        row2_col4.metric("IP", get_stat_value(stats_df, "inningsPitched"))

def add_rolling_metrics(game_logs_df, stat_group):
    df = game_logs_df.copy()

    if stat_group == "hitting":
        numeric_cols = ["AB", "H", "HR", "RBI", "BB", "SO"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["Rolling 7G AVG"] = (
            df["H"].rolling(7, min_periods=1).sum()
            / df["AB"].rolling(7, min_periods=1).sum()
        )

        df["Rolling 7G HR"] = df["HR"].rolling(7, min_periods=1).sum()
        df["Rolling 7G RBI"] = df["RBI"].rolling(7, min_periods=1).sum()
        df["Rolling 7G SO"] = df["SO"].rolling(7, min_periods=1).sum()

    elif stat_group == "pitching":
        numeric_cols = ["IP", "ER", "P_SO", "P_BB", "P_H", "P_HR"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["Rolling 5G SO"] = df["P_SO"].rolling(5, min_periods=1).sum()
        df["Rolling 5G ER"] = df["ER"].rolling(5, min_periods=1).sum()
        df["Rolling 5G IP"] = df["IP"].rolling(5, min_periods=1).sum()

    return df

def innings_to_outs(innings):
    """Convert baseball innings notation such as 6.2 into total outs."""
    if innings is None:
        return 0

    try:
        innings_str = str(innings)
        parts = innings_str.split(".")

        full_innings = int(parts[0])
        partial_outs = int(parts[1]) if len(parts) > 1 else 0

        return (full_innings * 3) + partial_outs
    except (ValueError, TypeError):
        return 0


def outs_to_innings(outs):
    """Convert total outs back to baseball innings notation."""
    full_innings = outs // 3
    remaining_outs = outs % 3

    return f"{full_innings}.{remaining_outs}"


def filter_recent_games(game_logs_df, period):
    df = game_logs_df.sort_values("Date").copy()

    periods = {
        "Last 7 Games": 7,
        "Last 15 Games": 15,
        "Last 30 Games": 30
    }

    if period == "Full Season":
        return df

    return df.tail(periods[period])


def calculate_split_summary(df, stat_group):
    if df.empty:
        return {}

    if stat_group == "hitting":
        numeric_cols = ["AB", "H", "HR", "RBI", "BB", "SO"]

        for col in numeric_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        ab = df["AB"].sum()
        hits = df["H"].sum()

        avg = hits / ab if ab > 0 else 0

        return {
            "Games": len(df),
            "AVG": f"{avg:.3f}".replace("0.", "."),
            "Hits": int(hits),
            "HR": int(df["HR"].sum()),
            "RBI": int(df["RBI"].sum()),
            "BB": int(df["BB"].sum()),
            "SO": int(df["SO"].sum())
        }

    else:
        numeric_cols = [
            "ER",
            "P_SO",
            "P_BB",
            "P_H"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        total_outs = df["IP"].apply(innings_to_outs).sum()
        innings = total_outs / 3

        earned_runs = df["ER"].sum()
        walks = df["P_BB"].sum()
        hits = df["P_H"].sum()

        era = (
            earned_runs * 9 / innings
            if innings > 0 else 0
        )

        whip = (
            (walks + hits) / innings
            if innings > 0 else 0
        )

        return {
            "Games": len(df),
            "IP": outs_to_innings(total_outs),
            "ERA": f"{era:.2f}",
            "WHIP": f"{whip:.2f}",
            "SO": int(df["P_SO"].sum()),
            "ER": int(earned_runs),
            "BB": int(walks)
        }


def create_monthly_splits(game_logs_df, stat_group):
    df = game_logs_df.copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    monthly_rows = []

    for month_date, month_df in df.groupby(
        pd.Grouper(key="Date", freq="MS")
    ):
        if month_df.empty:
            continue

        summary = calculate_split_summary(
            month_df.copy(),
            stat_group
        )

        summary["Month"] = month_date.strftime("%B")

        monthly_rows.append(summary)

    if not monthly_rows:
        return pd.DataFrame()

    monthly_df = pd.DataFrame(monthly_rows)

    # Put Month first
    columns = ["Month"] + [
        col for col in monthly_df.columns
        if col != "Month"
    ]

    return monthly_df[columns]

def show_player_explorer(
    search_players,
    get_player_season_stats,
    get_player_career_stats,
    get_player_team,
    get_player_game_logs,
    season
):
    st.header("👤 Player Explorer")

    player_name = st.text_input(
        "Search for a player",
        placeholder="Example: Aaron Judge"
    )

    if not player_name:
        st.info("Enter a player name to begin.")
        return

    results_df = search_players(player_name, season)

    if results_df.empty:
        st.warning("No players found.")
        return

    selected_name = st.selectbox(
        "Select Player",
        results_df["Name"].tolist()
    )

    player_row = results_df[
        results_df["Name"] == selected_name
    ].iloc[0]

    player_id = player_row["Player ID"]
    display_team = get_player_team(player_id, season)

    stat_group = st.radio(
        "Stat Type",
        ["hitting", "pitching"],
        horizontal=True
    )

    stats_view = st.radio(
        "Statistics View",
        ["Season Stats", "Career Stats"],
        horizontal=True
    )

    # Player profile card
    st.divider()

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.image(
            get_player_headshot_url(player_id),
            caption=selected_name,
            use_container_width=True
        )

    with right_col:
        st.markdown(f"## {selected_name}")

        profile_col1, profile_col2 = st.columns(2)

        with profile_col1:
            st.metric("Team", display_team)
            st.metric(
                "Position",
                player_row["Primary Position"]
            )
            st.metric("Bats", player_row["Bats"])

        with profile_col2:
            st.metric("Throws", player_row["Throws"])
            st.metric("Height", player_row["Height"])
            st.metric(
                "Weight",
                f"{player_row['Weight']} lbs"
            )

        st.markdown(
            f"**Birth Date:** {player_row['Birth Date']}"
        )

    st.divider()

    # ------------------------------------
    # SEASON STATS VIEW
    # ------------------------------------
    if stats_view == "Season Stats":
        stats_df, stats_team = get_player_season_stats(
            player_id,
            season,
            stat_group
        )

        if stats_df.empty:
            st.info(
                f"No {stat_group} stats found for "
                f"{selected_name} in {season}."
            )
            return

        st.subheader(f"{season} Season Statistics")

        show_featured_stat_cards(
            stats_df,
            stat_group
        )

        st.divider()

        st.subheader(
            f"Full {season} {stat_group.title()} Stat Table"
        )

        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Game logs only belong to season view
        st.subheader("📈 Game Log Trends")

        game_logs_df = get_player_game_logs(
            player_id,
            season,
            stat_group
        )

        if game_logs_df.empty:
            st.info(
                f"No game logs found for "
                f"{selected_name} in {season}."
            )
            return

        game_logs_df["Date"] = pd.to_datetime(
            game_logs_df["Date"],
            errors="coerce"
        )

        game_logs_df = game_logs_df.sort_values("Date")

        st.divider()

        st.subheader("🔎 Advanced Splits")

        recent_tab, monthly_tab = st.tabs([
            "Recent Performance",
            "Monthly Splits"
        ])

        with recent_tab:
            period = st.selectbox(
                "Performance Window",
                [
                    "Last 7 Games",
                    "Last 15 Games",
                    "Last 30 Games",
                    "Full Season"
                ],
                key="player_performance_window"
            )

            filtered_games = filter_recent_games(
                game_logs_df,
                period
            )

            summary = calculate_split_summary(
                filtered_games.copy(),
                stat_group
            )

            st.markdown(f"### {period}")

            if stat_group == "hitting":
                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Games", summary.get("Games", "N/A"))
                c2.metric("AVG", summary.get("AVG", "N/A"))
                c3.metric("Hits", summary.get("Hits", "N/A"))
                c4.metric("HR", summary.get("HR", "N/A"))

                c5, c6, c7 = st.columns(3)

                c5.metric("RBI", summary.get("RBI", "N/A"))
                c6.metric("BB", summary.get("BB", "N/A"))
                c7.metric("SO", summary.get("SO", "N/A"))

            else:
                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Games", summary.get("Games", "N/A"))
                c2.metric("IP", summary.get("IP", "N/A"))
                c3.metric("ERA", summary.get("ERA", "N/A"))
                c4.metric("WHIP", summary.get("WHIP", "N/A"))

                c5, c6, c7 = st.columns(3)

                c5.metric("SO", summary.get("SO", "N/A"))
                c6.metric("ER", summary.get("ER", "N/A"))
                c7.metric("BB", summary.get("BB", "N/A"))

        with monthly_tab:
            monthly_df = create_monthly_splits(
                game_logs_df,
                stat_group
            )

            if monthly_df.empty:
                st.info("No monthly split data available.")
            else:
                st.dataframe(
                    monthly_df,
                    use_container_width=True,
                    hide_index=True
                )

        st.divider()

        # ------------------------------------
        # GAME-BY-GAME TREND
        # ------------------------------------

        if stat_group == "hitting":
            chart_metric = st.selectbox(
                "Trend Metric",
                ["H", "HR", "RBI", "R", "BB", "SO"]
            )
        else:
            chart_metric = st.selectbox(
                "Trend Metric",
                ["IP", "ER", "P_SO", "P_BB", "P_H", "P_HR"]
            )

        fig = px.line(
            filtered_games,
            x="Date",
            y=chart_metric,
            markers=True,
            title=f"{selected_name}: {chart_metric} by Game",
            hover_data=["Opponent", "Team"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ------------------------------------
        # ROLLING PERFORMANCE TREND
        # ------------------------------------

        st.subheader("📈 Rolling Performance Trend")

        rolling_df = add_rolling_metrics(
            filtered_games,
            stat_group
        )

        if stat_group == "hitting":
            rolling_metric = st.selectbox(
                "Rolling Metric",
                [
                    "Rolling 7G AVG",
                    "Rolling 7G HR",
                    "Rolling 7G RBI",
                    "Rolling 7G SO"
                ]
            )
        else:
            rolling_metric = st.selectbox(
                "Rolling Metric",
                [
                    "Rolling 5G SO",
                    "Rolling 5G ER",
                    "Rolling 5G IP"
                ]
            )

        rolling_fig = px.line(
            rolling_df,
            x="Date",
            y=rolling_metric,
            markers=True,
            title=f"{selected_name}: {rolling_metric}",
            hover_data=["Opponent", "Team"]
        )

        st.plotly_chart(
            rolling_fig,
            use_container_width=True
        )

        # ------------------------------------
        # RECENT GAME LOG
        # ------------------------------------

        st.subheader("Recent Game Log")

        st.dataframe(
            filtered_games
            .tail(10)
            .sort_values("Date", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    # ------------------------------------
    # CAREER STATS VIEW
    # ------------------------------------
    else:
        career_stats_df = get_player_career_stats(
            player_id,
            stat_group
        )

        if career_stats_df.empty:
            st.info(
                f"No career {stat_group} stats found "
                f"for {selected_name}."
            )
            return

        st.subheader("Career Statistics")

        show_featured_stat_cards(
            career_stats_df,
            stat_group
        )

        st.divider()

        st.subheader(
            f"Full Career {stat_group.title()} Stat Table"
        )

        st.dataframe(
            career_stats_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Game logs and rolling trends are available "
            "only in the Season Stats view."
        )