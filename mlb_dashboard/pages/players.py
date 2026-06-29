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

def show_player_explorer(search_players, get_player_season_stats, get_player_team, get_player_game_logs, season):
    st.header("👤 Player Explorer")

    player_name = st.text_input("Search for a player", placeholder="Example: Aaron Judge")

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

    player_row = results_df[results_df["Name"] == selected_name].iloc[0]
    player_id = player_row["Player ID"]

    display_team = get_player_team(player_id, season)

    stat_group = st.radio(
        "Stat Type",
        ["hitting", "pitching"],
        horizontal=True
    )

    stats_df, stats_team = get_player_season_stats(player_id, season, stat_group)

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

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Team", display_team)
            st.metric("Position", player_row["Primary Position"])
            st.metric("Bats", player_row["Bats"])

        with col2:
            st.metric("Throws", player_row["Throws"])
            st.metric("Height", player_row["Height"])
            st.metric("Weight", f"{player_row['Weight']} lbs")

        st.markdown(f"**Birth Date:** {player_row['Birth Date']}")

    st.divider()

    if stats_df.empty:
        st.info(f"No {stat_group} stats found for {selected_name} in {season}.")
        return

    show_featured_stat_cards(stats_df, stat_group)

    st.divider()

    st.subheader(f"Full {season} {stat_group.title()} Stat Table")

    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📈 Game Log Trends")

    game_logs_df = get_player_game_logs(player_id, season, stat_group)

    if game_logs_df.empty:
        st.info(f"No game logs found for {selected_name} in {season}.")
        return

    game_logs_df["Date"] = pd.to_datetime(game_logs_df["Date"], errors="coerce")
    game_logs_df = game_logs_df.sort_values("Date")

    if stat_group == "hitting":
        chart_metric = st.selectbox(
            "Trend Metric",
            ["H", "HR", "RBI", "R", "BB", "SO"]
        )

        chart_title = f"{selected_name}: {chart_metric} by Game"

    else:
        chart_metric = st.selectbox(
            "Trend Metric",
            ["IP", "ER", "P_SO", "P_BB", "P_H", "P_HR"]
        )

        chart_title = f"{selected_name}: {chart_metric} by Game"

    fig = px.line(
        game_logs_df,
        x="Date",
        y=chart_metric,
        markers=True,
        title=chart_title,
        hover_data=["Opponent", "Team"]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Game Log")

    st.dataframe(
        game_logs_df.tail(10).sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )