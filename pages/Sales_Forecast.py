import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

from utils import (
    set_page_config,
    inject_css,
    page_header,
    styled_chart,
    PRIMARY,
    SUCCESS,
    ACCENT
)

# ------------------------------------------------
# Page Configuration
# ------------------------------------------------
set_page_config("Sales Forecast", "📈")
inject_css()

page_header(
    "📈 Revenue Forecasting",
    "Predict future monthly revenue using the Prophet forecasting model."
)
# ------------------------------------------------
# Load Model
# ------------------------------------------------
model = joblib.load("models/prophet_model.pkl")

months = st.slider(
    "Forecast Horizon (Months)",
    min_value=1,
    max_value=12,
    value=6
)

if st.button("Generate Revenue Forecast", use_container_width=True):

    with st.spinner("Generating revenue forecast..."):

        future = model.make_future_dataframe(
            periods=months,
            freq="M"
        )

        forecast = model.predict(future)

        forecast_future = forecast.tail(months)

    

    # -----------------------------
    # KPI Metrics
    # -----------------------------

    total_revenue = forecast_future["yhat"].sum()

    avg_revenue = forecast_future["yhat"].mean()

    max_month = forecast_future.loc[
        forecast_future["yhat"].idxmax(),
        "ds"
    ]

    max_revenue = forecast_future["yhat"].max()

    previous_month = forecast.iloc[-months-1]["yhat"]

    growth = ((avg_revenue - previous_month) /
              previous_month) * 100

    st.success("Forecast Generated Successfully!")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Predicted Revenue",
        f"£{total_revenue:,.0f}"
    )

    c2.metric(
        "Average Monthly Revenue",
        f"£{avg_revenue:,.0f}"
    )

    c3.metric(
        "Highest Revenue Month",
        max_month.strftime("%b %Y")
    )

    c4.metric(
        "Growth",
        f"{growth:.2f}%"
    )
    st.markdown(
    f"""
### 📌 Forecast Summary

The model predicts a **total revenue of £{total_revenue:,.0f}**
over the next **{months} months** with an average monthly revenue
of **£{avg_revenue:,.0f}**.
"""
)

    st.markdown("---")

    # -----------------------------
    # Forecast Chart
    # -----------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            name="Forecast Revenue",
            line=dict(
                color=PRIMARY,
                width=3
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            line=dict(width=0),
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            fill="tonexty",
            line=dict(width=0),
            name="Confidence Interval"
        )
    )

    fig = styled_chart(fig, 500)

    fig.update_layout(
        title="Historical + Forecast Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Forecast Table
    # -----------------------------

    st.markdown("## 📅 Revenue Forecast")

    table = forecast_future[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ].copy()

    table.columns = [
        "Month",
        "Predicted Revenue",
        "Lower Bound",
        "Upper Bound"
    ]

    table["Predicted Revenue"] = table["Predicted Revenue"].round(2)

    table["Lower Bound"] = table["Lower Bound"].round(2)

    table["Upper Bound"] = table["Upper Bound"].round(2)

    st.dataframe(
        table,
        use_container_width=True
    )

    # -----------------------------
    # Business Insights
    # -----------------------------

    st.markdown("## 💡 Business Insights")

    st.info(f"""
**Forecast Summary**

• Expected revenue over the next **{months} months** is **£{total_revenue:,.0f}**.

• Average monthly revenue is expected to be **£{avg_revenue:,.0f}**.

• Highest predicted revenue occurs in **{max_month.strftime('%B %Y')}**
with approximately **£{max_revenue:,.0f}**.

• Expected month-over-month growth is **{growth:.2f}%**.

**Business Recommendation**

• Prepare inventory based on the projected demand.

• Allocate marketing budget before peak months.

• Ensure sufficient stock availability during the forecasted high-revenue period.
""")

    # -----------------------------
    # Download
    # -----------------------------

    csv = table.to_csv(index=False)

    st.download_button(
        "⬇ Download Forecast Report",
        csv,
        "Revenue_Forecast.csv",
        "text/csv"
    )
    st.markdown("---")

st.caption(
    """
    Forecasts are generated using the **Meta Prophet** forecasting model
    trained on historical monthly sales data.

    These predictions are intended to support business planning,
    budgeting, inventory management, and demand forecasting.
    """
)