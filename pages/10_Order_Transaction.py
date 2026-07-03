import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Order & Transaction", "🧾")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("🧾 Order & Transaction Dashboard", "Order-level analysis: size, value, and patterns")

inv = (df.groupby("Invoice")
         .agg(Revenue=("Sales","sum"),
              Items=("StockCode","nunique"),
              Quantity=("Quantity","sum"),
              Customer=("Customer ID","first"),
              Country=("Country","first"),
              Date=("InvoiceDate","first"),
              Month=("Month","first"),
              Year=("Year","first"),
              Weekday=("Weekday","first"),
              Hour=("Hour","first"))
         .reset_index())

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Orders",       f"{len(inv):,}")
with k2: st.metric("Avg Order Value",    f"£{inv['Revenue'].mean():,.2f}")
with k3: st.metric("Median Order Value", f"£{inv['Revenue'].median():,.2f}")
with k4: st.metric("Avg Items/Order",    f"{inv['Items'].mean():.1f}")
with k5: st.metric("Avg Qty/Order",      f"{inv['Quantity'].mean():.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# Order value distribution + cumulative
c1, c2 = st.columns(2)
with c1:
    section_header("📊 Order Value Distribution")
    cap = inv[inv["Revenue"] <= inv["Revenue"].quantile(0.95)]["Revenue"]
    fig = go.Figure(go.Histogram(
        x=cap, nbinsx=60,
        marker=dict(color=PRIMARY, line=dict(color="#0D0D1A", width=0.5)),
    ))
    fig = styled_chart(fig, 310)
    fig.update_layout(xaxis_title="Order Value (£)", yaxis_title="# Orders")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("📦 Items per Order Distribution")
    cap2 = inv[inv["Items"] <= inv["Items"].quantile(0.98)]["Items"]
    fig2 = go.Figure(go.Histogram(
        x=cap2, nbinsx=40,
        marker=dict(color=SECONDARY, line=dict(color="#0D0D1A", width=0.5)),
    ))
    fig2 = styled_chart(fig2, 310)
    fig2.update_layout(xaxis_title="Unique Items per Order", yaxis_title="# Orders")
    st.plotly_chart(fig2, use_container_width=True)

# Orders over time
section_header("📈 Daily Order Volume")
daily_orders = inv.groupby("Date").size().reset_index(name="Orders").sort_values("Date")
daily_orders["Rolling7"] = daily_orders["Orders"].rolling(7).mean()
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=daily_orders["Date"], y=daily_orders["Orders"],
                      marker=dict(color="rgba(79,70,229,0.4)"), name="Daily Orders"))
fig3.add_trace(go.Scatter(x=daily_orders["Date"], y=daily_orders["Rolling7"],
                           mode="lines", name="7-Day Avg",
                           line=dict(color=ACCENT, width=2)))
fig3 = styled_chart(fig3, 320)
st.plotly_chart(fig3, use_container_width=True)

# By weekday + hour
c3, c4 = st.columns(2)
DAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

with c3:
    section_header("📅 Orders by Day of Week")
    day_ord = inv.groupby("Weekday").size().reindex(DAY_ORDER).reset_index(name="Orders")
    fig4 = go.Figure(go.Bar(
        x=day_ord["Weekday"], y=day_ord["Orders"],
        marker=dict(color=PALETTE[:7]),
    ))
    fig4 = styled_chart(fig4, 280)
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    section_header("⏰ Orders by Hour")
    hour_ord = inv.groupby("Hour").size().reset_index(name="Orders").sort_values("Hour")
    hour_ord["Label"] = hour_ord["Hour"].astype(str).str.zfill(2) + ":00"
    fig5 = go.Figure(go.Bar(
        x=hour_ord["Label"], y=hour_ord["Orders"],
        marker=dict(color=ACCENT),
    ))
    fig5 = styled_chart(fig5, 280)
    st.plotly_chart(fig5, use_container_width=True)

# Order value by country (Top 10)
section_header("🌍 Avg Order Value by Country (Top 10)")
country_aov = inv.groupby("Country")["Revenue"].mean().sort_values(ascending=False).head(10).reset_index()
fig6 = go.Figure(go.Bar(
    x=country_aov["Revenue"], y=country_aov["Country"],
    orientation="h",
    marker=dict(color=SUCCESS),
    hovertemplate="<b>%{y}</b><br>AOV: £%{x:,.2f}<extra></extra>"
))
fig6 = styled_chart(fig6, 320)
fig6.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="Avg Order Value (£)")
st.plotly_chart(fig6, use_container_width=True)

# Top 20 orders table
section_header("🏆 Top 20 Highest-Value Orders")
top20 = inv.sort_values("Revenue", ascending=False).head(20).copy()
top20["Revenue"]  = top20["Revenue"].map("£{:,.2f}".format)
top20["Customer"] = top20["Customer"].astype(str)
top20 = top20[["Invoice","Date","Customer","Country","Items","Quantity","Revenue"]]
top20.columns = ["Invoice","Date","Customer","Country","Items","Qty","Revenue"]
st.dataframe(top20.reset_index(drop=True), use_container_width=True, height=350)
