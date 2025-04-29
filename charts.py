import pandas as pd
import streamlit as st
import plotly.express as px


def creating_sessions_chart(
    df: pd.DataFrame,
    measure_column: str,
    unique_key: str,
    tag_column: str = "tag",  # column that holds the tag
    sku_column: str = "SKU",  # column that holds the ASIN / SKU
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
        df[[tag_column, sku_column]]
        .drop_duplicates()  # unique (tag, ASIN) pairs
        .groupby(tag_column)[sku_column]
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
        key=f"{unique_key}_1",
    )

    date_min, date_max = st.date_input(
        "Date range",
        [df[date_column].min(), df[date_column].max()],
        key=f"{unique_key}_2",
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
        y=measure_column,
        color=sku_column,
        trendline="ols",
        trendline_scope="group",
        labels={
            date_column: "Date",
            measure_column: "Sessions",
            sku_column: "ASIN / SKU",
        },
        title=f"Sessions Over Time – {', '.join(selected_tags)}",
    )

    fig.update_traces(mode="lines+markers")
    fig.update_xaxes(dtick="D1", tickformat="%Y-%m-%d", tickangle=45)
    fig.update_layout(showlegend=True)

    # put the ASIN label to the right‑most point of each line
    for asin, df_asin in filtered.groupby(sku_column):
        last_point = df_asin.sort_values(date_column).iloc[-1]
        fig.add_annotation(
            x=last_point[date_column],
            y=last_point[measure_column],
            text=asin,
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=11),
        )

    st.plotly_chart(fig, use_container_width=True, key=f"{unique_key}_3")
