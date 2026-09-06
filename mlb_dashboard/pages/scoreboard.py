import plotly.express as px
import streamlit as st


def show_daily_scoreboard(cached_schedule):
    st.header("📅 Daily Scoreboard")

    selected_date = st.date_input("Select Date")

    df = cached_schedule(
        selected_date.strftime("%Y-%m-%d")
    )

    if df.empty:
        st.warning("No games found for this date.")
        return

    display_df = df.copy()

    display_df["Away Score"] = (
        display_df["Away Score"].fillna("")
    )

    display_df["Home Score"] = (
        display_df["Home Score"].fillna("")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    scored_games = df.dropna(
        subset=["Away Score", "Home Score"]
    ).copy()

    if scored_games.empty:
        st.info(
            "No scored games yet for this date."
        )
        return

    scored_games["Away Score"] = (
        scored_games["Away Score"].astype(int)
    )

    scored_games["Home Score"] = (
        scored_games["Home Score"].astype(int)
    )

    chart_df = scored_games.melt(
        id_vars=["Game"],
        value_vars=[
            "Away Score",
            "Home Score"
        ],
        var_name="Team Type",
        value_name="Runs"
    )

    fig = px.bar(
        chart_df,
        x="Game",
        y="Runs",
        color="Team Type",
        barmode="group",
        title="Runs by Game"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )