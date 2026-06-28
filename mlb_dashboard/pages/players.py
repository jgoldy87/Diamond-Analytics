import streamlit as st


def get_player_headshot_url(player_id):
    return f"https://img.mlbstatic.com/mlb-photos/image/upload/w_240,q_100/v1/people/{player_id}/headshot/67/current"


def show_player_explorer(search_players, get_player_season_stats, get_player_team, season):
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

    st.subheader(f"{season} {stat_group.title()} Stats")

    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True
    )