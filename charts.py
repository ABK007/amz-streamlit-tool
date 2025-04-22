import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import streamlit as st
import plotly.express as px
import math
import uuid


def create_linear_regression_chart(df):
    # 1) Ensure date→datetime and numeric
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df["date_num"] = df["date"].map(lambda d: d.toordinal())

    # 2) Figure out grid dimensions
    asins = df["SKU"].unique()
    n_asins = len(asins)
    ncols = 2
    nrows = math.ceil(n_asins / ncols)

    # 3) Create a grid of subplots
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 6 * nrows),  # width = 6" per column, height = 4" per row
        sharex=True,
        sharey=True,
    )
    axes = axes.flatten()  # so we can index 0…n_asins‑1

    # 4) Loop once over each ASIN & its dedicated Axes
    for ax, asin in zip(axes, asins):
        group = df[df["SKU"] == asin]

        # a) regression inputs
        X = group["date_num"].values.reshape(-1, 1)
        y = group["Sessions - Total"].values

        # b) fit & scatter
        model = LinearRegression().fit(X, y)
        ax.scatter(group["date"], y, alpha=0.6)

        # c) draw trend line across full date range
        dr = pd.date_range(group["date"].min(), group["date"].max(), freq="D")
        dr_num = dr.map(lambda d: d.toordinal()).values.reshape(-1, 1)
        ax.plot(dr, model.predict(dr_num), lw=2)

        # d) titles & labels
        ax.set_title(f"ASIN: {asin}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sessions")

    # 5) Hide any empty subplots (odd number of ASINs)
    for empty_ax in axes[n_asins:]:
        empty_ax.set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)


def creating_plotly_chart(
    df: pd.DataFrame,
    tag_column: str = "tag",  # column that holds the tag
    asin_column: str = "SKU",  # column that holds the ASIN / SKU
    date_column: str = "date",
) -> None:
    """
    Render a Plotly scatter/line chart of Sessions‑Total over time for all
    ASINs whose *tag* is chosen in the Streamlit UI.

    Only tags that occur on ≥ 2 distinct ASINs are shown in the selector.
    """

    df[date_column] = pd.to_datetime(
        df[date_column]
    )  # ensuring the column is true datetime64
    # ------------------------------------------------------------------
    # 1) Build the list of tags that are *not* unique
    # ------------------------------------------------------------------
    tag_counts = (
        df[[tag_column, asin_column]]
        .drop_duplicates()  # unique (tag, ASIN) pairs
        .groupby(tag_column)[asin_column]
        .nunique()  # number of distinct ASINs per tag
    )  # -> index is ordinary Index

    non_unique_tags = tag_counts[tag_counts > 1].index.tolist()
    if not non_unique_tags:  # defensive guard
        st.info("Every tag is linked to a single ASIN; nothing to filter.")
        return

    # ------------------------------------------------------------------
    # 2) Streamlit widgets
    # ------------------------------------------------------------------
    selected_tags = st.multiselect(
        "Select tag(s) that appear on more than one ASIN",
        options=non_unique_tags,
        default=non_unique_tags,  # show everything at start
        key=f"tag_selector_{tag_column}",
    )

    date_min, date_max = st.date_input(
        "Date range",
        [df[date_column].min(), df[date_column].max()],
        key=f"date_range_{tag_column}",
    )

    # ------------------------------------------------------------------
    # 3) Filter rows
    #    a) keep only chosen tags
    #    b) keep dates inside the range
    # ------------------------------------------------------------------
    filtered = df[
        (df[tag_column].isin(selected_tags))
        & (df[date_column] >= pd.to_datetime(date_min))
        & (df[date_column] <= pd.to_datetime(date_max))
    ]

    # quick exit if nothing left
    if filtered.empty:
        st.warning("No rows match the current filters.")
        return

    # ------------------------------------------------------------------
    # 4) Build the figure – colour by ASIN / SKU
    # ------------------------------------------------------------------
    fig = px.scatter(
        filtered,
        x=date_column,
        y="Sessions - Total",
        color=asin_column,
        trendline="ols",
        trendline_scope="group",
        labels={
            date_column: "Date",
            "Sessions - Total": "Sessions",
            asin_column: "ASIN / SKU",
        },
        title=f"Sessions Over Time – {', '.join(selected_tags)}",
    )

    fig.update_traces(mode="lines+markers")
    fig.update_xaxes(dtick="D1", tickformat="%Y-%m-%d", tickangle=45)
    fig.update_layout(showlegend=True)

    # put the ASIN label to the right‑most point of each line
    for asin, df_asin in filtered.groupby(asin_column):
        last_point = df_asin.sort_values(date_column).iloc[-1]
        fig.add_annotation(
            x=last_point[date_column],
            y=last_point["Sessions - Total"],
            text=asin,
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=11),
        )

    st.plotly_chart(fig, use_container_width=True)
