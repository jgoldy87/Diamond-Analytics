import streamlit as st
import plotly.express as px

def show_division_standings(df):
    st.header("📊 Division Standings")

    league_filter = st.selectbox(
        "League",
        ["All MLB", "American League", "National League"]
    )

    if league_filter != "All MLB":
        df = df[df["League"] == league_filter]

    for division in sorted(df["Division"].unique()):
        st.subheader(division)

        div_df = (
            df[df["Division"] == division]
            .sort_values(["Wins", "Pct"], ascending=False)
            [[
                "Team",
                "Wins",
                "Losses",
                "Pct",
                "GB",
                "Run Differential",
                "Streak"
            ]]
        )

        st.dataframe(div_df, use_container_width=True, hide_index=True)

        fig = px.scatter(
            div_df,
            x="Wins",
            y="Run Differential",
            text="Team",
            size="Pct",
            hover_data=["Losses", "GB", "Streak"],
            title=f"{division}: Wins vs Run Differential"
        )

        fig.update_traces(textposition="top center")

        st.plotly_chart(fig, use_container_width=True)


def show_wild_card_standings(df):
    st.header("🔥 Wild Card Standings")

    for league in ["American League", "National League"]:
        st.subheader(league)

        league_df = df[df["League"] == league].copy()

        # Remove division leaders
        division_leaders = (
            league_df.sort_values(["Division", "Wins", "Pct"], ascending=[True, False, False])
            .groupby("Division")
            .head(1)["Team"]
            .tolist()
        )

        wc_df = league_df[~league_df["Team"].isin(division_leaders)].copy()

        # Sort Wild Card race manually
        wc_df = wc_df.sort_values(["Wins", "Pct", "Run Differential"], ascending=False).reset_index(drop=True)

        top_wins = wc_df.loc[0, "Wins"] if not wc_df.empty else 0
        top_losses = wc_df.loc[0, "Losses"] if not wc_df.empty else 0

        wc_df["Wild Card Rank"] = wc_df.index + 1
        wc_df["Calculated WC GB"] = wc_df.apply(
            lambda row: ((top_wins - row["Wins"]) + (row["Losses"] - top_losses)) / 2,
            axis=1
        )

        wc_df["Calculated WC GB"] = wc_df["Calculated WC GB"].apply(
            lambda x: "-" if x == 0 else x
        )

        display_df = wc_df[[
            "Wild Card Rank",
            "Team",
            "Wins",
            "Losses",
            "Pct",
            "Calculated WC GB",
            "Run Differential",
            "Streak"
        ]]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        chart_df = display_df.copy()
    
    chart_df["WC GB Numeric"] = chart_df["Calculated WC GB"].replace("-", 0)
    chart_df["WC GB Numeric"] = chart_df["WC GB Numeric"].astype(float)

    fig = px.scatter(
        chart_df,
        x="Wins",
        y="WC GB Numeric",
        text="Team",
        size="Pct",
        hover_data=["Losses", "Run Differential", "Streak"],
        title=f"{league}: Wild Card Positioning"
    )

    fig.update_traces(textposition="top center")
    fig.update_yaxes(title="Games Back", autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)