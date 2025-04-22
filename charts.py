

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import streamlit as st
import plotly.express as px
import math


def create_linear_regression_chart(df):
    # 1) Ensure date→datetime and numeric
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    df['date_num'] = df['date'].map(lambda d: d.toordinal())

    # 2) Figure out grid dimensions
    asins = df['(Child) ASIN'].unique()
    n_asins = len(asins)
    ncols = 2
    nrows = math.ceil(n_asins / ncols)

    # 3) Create a grid of subplots
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 6 * nrows),  # width = 6" per column, height = 4" per row
        sharex=True,
        sharey=True
    )
    axes = axes.flatten()  # so we can index 0…n_asins‑1

    # 4) Loop once over each ASIN & its dedicated Axes
    for ax, asin in zip(axes, asins):
        group = df[df['(Child) ASIN'] == asin]

        # a) regression inputs
        X = group['date_num'].values.reshape(-1,1)
        y = group['Sessions - Total'].values

        # b) fit & scatter
        model = LinearRegression().fit(X, y)
        ax.scatter(group['date'], y, alpha=0.6)

        # c) draw trend line across full date range
        dr = pd.date_range(group['date'].min(), group['date'].max(), freq='D')
        dr_num = dr.map(lambda d: d.toordinal()).values.reshape(-1,1)
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
    
    
def creating_plotly_chart(df):
    """This function creates dynamic plotly liner 
    chart and allows user to filter by ASIN and date range.
    
    param df: DataFrame
    
    return: None"""
    

    
    chosen_asins = st.multiselect(
        "Select ASIN(s)", options=df["(Child) ASIN"].unique(), default=df["(Child) ASIN"].unique()
    )
    date_min, date_max = st.date_input(
        "Date range", [df["date"].min(), df["date"].max()]
    )

    
    mask = (
        df["(Child) ASIN"].isin(chosen_asins)
        & (df["date"] >= pd.to_datetime(date_min).date())
        & (df["date"] <= pd.to_datetime(date_max).date())
    )
    filtered = df.loc[mask]

    # — build the Plotly Express figure —
    fig = px.scatter(
        filtered,
        x="date",
        y="Sessions - Total",
        color="(Child) ASIN",
        trendline="ols",            # automatically fit one OLS line per ASIN
        trendline_scope="group",    # group by ASIN
        labels={"date":"Date", "Sessions - Total":"Sessions"},
        title="Sessions Over Time by ASIN"
    )

    # show both markers & lines
    fig.update_traces(mode="lines+markers")

    # format the x-axis to show only date
    fig.update_xaxes(
        dtick="D1",
        tickformat="%Y-%m-%d",
        tickangle=45
    )

    fig.update_layout(showlegend=False)
    
    for asin in filtered["(Child) ASIN"].unique():
        df_asin = filtered[filtered["(Child) ASIN"] == asin].sort_values("date")
        last = df_asin.iloc[-1]
        fig.add_annotation(
            x=last["date"],
            y=last["Sessions - Total"],
            text=asin,
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=12)
        )

    # — render in Streamlit —
    st.plotly_chart(fig, use_container_width=True)


