import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Advanced Analytics", "🔬")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("🔬 Advanced Analytics Dashboard", "Cohort analysis, basket size, growth rates and cross-metrics")

# ── Cohort Analysis ───────────────────────────────────────────────────────────
section_header("👥 Monthly Customer Cohort — Retention Rate")

df_c = df.copy()
df_c["InvoiceDate"] = pd.to_datetime(df_c["InvoiceDate"])
df_c["YM"] = df_c["InvoiceDate"].dt.to_period("M")

cust_first = df_c.groupby("Customer ID")["YM"].min().reset_index()
cust_first.columns = ["Customer ID","CohortMonth"]
df_c = df_c.merge(cust_first, on="Customer ID")
df_c["CohortIndex"] = (df_c["YM"].astype(int) - df_c["CohortMonth"].astype(int))

cohort_data = (df_c.groupby(["CohortMonth","CohortIndex"])["Customer ID"]
                   .nunique().reset_index())
cohort_pivot = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="Customer ID")
cohort_pct   = cohort_pivot.div(cohort_pivot[0], axis=0).round(3) * 100

# limit to last 12 cohorts for readability
cohort_pct_display = cohort_pct.iloc[-12:, :12].fillna(0)
cohort_pct_display.index = cohort_pct_display.index.astype(str)

fig_cohort = go.Figure(go.Heatmap(
    z=cohort_pct_display.values,
    x=[f"Month {i}" for i in range(12)],
    y=cohort_pct_display.index.tolist(),
    colorscale="Blues",
    text=[[f"{v:.0f}%" if v > 0 else "" for v in row] for row in cohort_pct_display.values],
    texttemplate="%{text}",
    textfont=dict(size=10, color="white"),
    hovertemplate="Cohort: %{y}<br>%{x}<br>Retention: %{z:.1f}%<extra></extra>",
    zmin=0, zmax=100,
))
fig_cohort.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#CBD5E1"), height=400,
    margin=dict(l=0,r=0,t=30,b=0),
    xaxis=dict(side="bottom"),
    coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"))
)
st.plotly_chart(fig_cohort, use_container_width=True)

# ── Basket size over time ─────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    section_header("🛒 Average Basket Size Over Time (Items/Order)")
    inv_items = df.groupby(["Invoice","Year","Month"])["StockCode"].nunique().reset_index()
    inv_items.columns = ["Invoice","Year","Month","Items"]
    monthly_basket = inv_items.groupby(["Year","Month"])["Items"].mean().reset_index()
    monthly_basket["Period"] = monthly_basket["Year"].astype(str) + "-" + monthly_basket["Month"].astype(str).str.zfill(2)
    monthly_basket = monthly_basket.sort_values(["Year","Month"])
    fig2 = go.Figure(go.Scatter(
        x=monthly_basket["Period"], y=monthly_basket["Items"],
        mode="lines+markers",
        line=dict(color=SECONDARY, width=2),
        marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.1)",
    ))
    fig2 = styled_chart(fig2, 300)
    fig2.update_xaxes(tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    section_header("📊 Revenue per Customer Over Time")
    cust_monthly = df.groupby(["Year","Month"]).agg(
        Revenue=("Sales","sum"), Customers=("Customer ID","nunique")).reset_index()
    cust_monthly["RevenuePerCust"] = cust_monthly["Revenue"] / cust_monthly["Customers"]
    cust_monthly["Period"] = cust_monthly["Year"].astype(str) + "-" + cust_monthly["Month"].astype(str).str.zfill(2)
    cust_monthly = cust_monthly.sort_values(["Year","Month"])
    fig3 = go.Figure(go.Scatter(
        x=cust_monthly["Period"], y=cust_monthly["RevenuePerCust"],
        mode="lines+markers",
        line=dict(color=ACCENT, width=2),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.1)",
    ))
    fig3 = styled_chart(fig3, 300)
    fig3.update_xaxes(tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

# ── Top country growth ────────────────────────────────────────────────────────
section_header("🌍 Country Revenue — Year-over-Year Growth")
country_yoy = df.groupby(["Country","Year"])["Sales"].sum().reset_index()
country_yoy_pivot = country_yoy.pivot(index="Country", columns="Year", values="Sales").fillna(0)
top_countries = df.groupby("Country")["Sales"].sum().sort_values(ascending=False).head(12).index
country_yoy_top = country_yoy_pivot.loc[country_yoy_pivot.index.isin(top_countries)]

years = sorted(df["Year"].unique())
if len(years) >= 2:
    last_y  = years[-1]
    prev_y  = years[-2]
    if prev_y in country_yoy_top.columns and last_y in country_yoy_top.columns:
        country_yoy_top["Growth%"] = ((country_yoy_top[last_y] - country_yoy_top[prev_y]) /
                                       country_yoy_top[prev_y].replace(0,1)) * 100
        growth_df = country_yoy_top["Growth%"].reset_index().sort_values("Growth%", ascending=False)
        colors_g  = [SUCCESS if v >= 0 else DANGER for v in growth_df["Growth%"]]
        fig4 = go.Figure(go.Bar(
            x=growth_df["Country"], y=growth_df["Growth%"],
            marker=dict(color=colors_g),
            hovertemplate="<b>%{x}</b><br>YoY Growth: %{y:.1f}%<extra></extra>"
        ))
        fig4.add_hline(y=0, line_color="#475569")
        fig4 = styled_chart(fig4, 320)
        st.plotly_chart(fig4, use_container_width=True)

# ── Product cross-metrics bubble ─────────────────────────────────────────────
section_header("🔬 Product Intelligence: Price × Volume × Revenue")
prod_adv = (df.groupby("Description")
              .agg(AvgPrice=("Price","mean"),
                   TotalQty=("Quantity","sum"),
                   TotalRevenue=("Sales","sum"),
                   OrderCount=("Invoice","nunique"))
              .reset_index())
prod_adv = prod_adv[prod_adv["AvgPrice"] <= prod_adv["AvgPrice"].quantile(0.97)].head(100)
prod_adv["Label"] = prod_adv["Description"].str[:20]
fig5 = px.scatter(
    prod_adv, x="AvgPrice", y="TotalQty",
    size="TotalRevenue",
    color="OrderCount",
    color_continuous_scale="Magma",
    hover_name="Label",
    labels={"AvgPrice":"Avg Price (£)","TotalQty":"Qty Sold","TotalRevenue":"Revenue","OrderCount":"Orders"},
    size_max=45,
)
fig5 = styled_chart(fig5, 420)
fig5.update_layout(coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"), title=dict(text="Orders", font=dict(color="#94A3B8"))))
st.plotly_chart(fig5, use_container_width=True)
