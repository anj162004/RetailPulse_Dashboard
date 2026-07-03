import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Sales Trend Analysis", "📈")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("📈 Sales Trend Analysis", "Monthly, quarterly and yearly revenue patterns")

# KPIs
k1, k2, k3, k4 = st.columns(4)
monthly = df.groupby(["Year","Month"])["Sales"].sum().reset_index()
best_month = monthly.loc[monthly["Sales"].idxmax()]
worst_month = monthly.loc[monthly["Sales"].idxmin()]
with k1: st.metric("Total Revenue", f"£{df['Sales'].sum():,.0f}")
with k2: st.metric("Avg Monthly Revenue", f"£{monthly['Sales'].mean():,.0f}")
with k3: st.metric("Best Month", f"{int(best_month['Year'])}-M{int(best_month['Month'])}", f"£{best_month['Sales']:,.0f}")
with k4: st.metric("Worst Month", f"{int(worst_month['Year'])}-M{int(worst_month['Month'])}", f"£{worst_month['Sales']:,.0f}", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ── Full trend line ───────────────────────────────────────────────────────────
section_header("📊 Full Revenue Timeline (Monthly)")
monthly_sorted = monthly.sort_values(["Year","Month"])
monthly_sorted["Period"] = monthly_sorted["Year"].astype(str) + "-" + monthly_sorted["Month"].astype(str).str.zfill(2)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=monthly_sorted["Period"], y=monthly_sorted["Sales"],
    mode="lines+markers",
    line=dict(color=PRIMARY, width=2.5),
    marker=dict(size=6, color=PRIMARY),
    fill="tozeroy", fillcolor="rgba(79,70,229,0.1)",
    name="Monthly Revenue",
    hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>"
))
# 3-month rolling average
monthly_sorted["Rolling3"] = monthly_sorted["Sales"].rolling(3).mean()
fig.add_trace(go.Scatter(
    x=monthly_sorted["Period"], y=monthly_sorted["Rolling3"],
    mode="lines", name="3M Rolling Avg",
    line=dict(color=ACCENT, width=2, dash="dot"),
))
fig = styled_chart(fig, 380)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# ── Quarterly + YoY breakdown ─────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    section_header("📅 Quarterly Revenue")
    df["Quarter"] = "Q" + pd.to_datetime(df["InvoiceDate"]).dt.quarter.astype(str)
    qtr = df.groupby(["Year","Quarter"])["Sales"].sum().reset_index()
    fig2 = px.bar(qtr, x="Quarter", y="Sales", color="Year",
                  barmode="group",
                  color_discrete_sequence=PALETTE)
    fig2 = styled_chart(fig2, 330)
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    section_header("📆 Monthly Seasonality (Avg across years)")
    mn_order = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"]
    seasonal = df.groupby("MonthName")["Sales"].mean().reindex(mn_order).reset_index()
    fig3 = go.Figure(go.Bar(
        x=seasonal["MonthName"], y=seasonal["Sales"],
        marker=dict(color=PALETTE[:12]),
    ))
    fig3 = styled_chart(fig3, 330)
    fig3.update_xaxes(tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

# ── Growth rate ────────────────────────────────────────────────────────────────
section_header("📈 Month-over-Month Growth Rate (%)")
monthly_sorted["MoM_growth"] = monthly_sorted["Sales"].pct_change() * 100
fig4 = go.Figure()
colors_bar = [SUCCESS if v >= 0 else DANGER for v in monthly_sorted["MoM_growth"].fillna(0)]
fig4.add_trace(go.Bar(
    x=monthly_sorted["Period"],
    y=monthly_sorted["MoM_growth"],
    marker=dict(color=colors_bar),
    hovertemplate="<b>%{x}</b><br>MoM Growth: %{y:.1f}%<extra></extra>"
))
fig4.add_hline(y=0, line_color="#475569", line_width=1)
fig4 = styled_chart(fig4, 300)
fig4.update_xaxes(tickangle=-45)
st.plotly_chart(fig4, use_container_width=True)
