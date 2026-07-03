import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Customer Analytics", "👥")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("👥 Customer Analytics Dashboard", "Spend patterns, segmentation and loyalty analysis")

cust = (df.groupby("Customer ID")
          .agg(OrderCount=("Invoice","nunique"),
               TotalSpend=("Sales","sum"),
               TotalQty=("Quantity","sum"),
               AvgOrderValue=("Sales","mean"),
               UniqueProducts=("StockCode","nunique"))
          .reset_index()
          .sort_values("TotalSpend", ascending=False))

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Customers", f"{len(cust):,}")
with k2: st.metric("Top Customer Revenue", f"£{cust['TotalSpend'].iloc[0]:,.0f}")
with k3: st.metric("Avg Spend/Customer", f"£{cust['TotalSpend'].mean():,.0f}")
with k4: st.metric("Avg Orders/Customer", f"{cust['OrderCount'].mean():.1f}")
with k5: st.metric("Avg Order Value", f"£{cust['AvgOrderValue'].mean():,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    section_header("🏆 Top 15 Customers by Revenue")
    top15 = cust.head(15).copy()
    top15["CID"] = "Cust #" + top15["Customer ID"].astype(str)
    fig = go.Figure(go.Bar(
        x=top15["TotalSpend"], y=top15["CID"],
        orientation="h",
        marker=dict(color=PALETTE[:15]),
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>"
    ))
    fig = styled_chart(fig, 420)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("🔄 Top 15 Customers by Order Frequency")
    top15f = cust.sort_values("OrderCount", ascending=False).head(15).copy()
    top15f["CID"] = "Cust #" + top15f["Customer ID"].astype(str)
    fig2 = go.Figure(go.Bar(
        x=top15f["OrderCount"], y=top15f["CID"],
        orientation="h",
        marker=dict(color=SECONDARY),
        hovertemplate="<b>%{y}</b><br>Orders: %{x:,}<extra></extra>"
    ))
    fig2 = styled_chart(fig2, 420)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Spend distribution histogram
section_header("📊 Customer Spend Distribution")
c3, c4 = st.columns(2)
with c3:
    spend_cap = cust[cust["TotalSpend"] <= cust["TotalSpend"].quantile(0.95)]["TotalSpend"]
    fig3 = go.Figure(go.Histogram(
        x=spend_cap, nbinsx=50,
        marker=dict(color=ACCENT, line=dict(color="#0D0D1A", width=0.5)),
    ))
    fig3 = styled_chart(fig3, 300)
    fig3.update_layout(xaxis_title="Total Spend (£)", yaxis_title="Customer Count")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    section_header("🥧 Customer Value Segments")
    p25  = cust["TotalSpend"].quantile(0.25)
    p75  = cust["TotalSpend"].quantile(0.75)
    low  = cust[cust["TotalSpend"] <  p25]
    mid  = cust[(cust["TotalSpend"] >= p25) & (cust["TotalSpend"] < p75)]
    high = cust[cust["TotalSpend"] >= p75]
    fig4 = go.Figure(go.Pie(
        labels=["Low Value","Mid Value","High Value"],
        values=[len(low), len(mid), len(high)],
        marker=dict(colors=[DANGER, ACCENT, SUCCESS]),
        hole=0.5,
    ))
    fig4 = styled_chart(fig4, 300)
    st.plotly_chart(fig4, use_container_width=True)

# Scatter: orders vs spend
section_header("🔍 Order Frequency vs Total Spend (per Customer)")
fig5 = px.scatter(
    cust, x="OrderCount", y="TotalSpend",
    color="AvgOrderValue",
    color_continuous_scale="Viridis",
    size="UniqueProducts",
    hover_data={"Customer ID": True},
    labels={"OrderCount":"Orders", "TotalSpend":"Total Spend (£)", "AvgOrderValue":"Avg Order £"},
    size_max=20,
)
fig5 = styled_chart(fig5, 370)
fig5.update_layout(coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"), title=dict(text="Avg Order £", font=dict(color="#94A3B8"))))
st.plotly_chart(fig5, use_container_width=True)
