import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Monthly & Seasonal Sales", "📅")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("📅 Monthly & Seasonal Sales Dashboard", "Seasonal patterns, peak periods and time-based trends")

MONTH_ORDER = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
DAY_ORDER   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# KPIs
k1,k2,k3,k4 = st.columns(4)
monthly_total  = df.groupby("MonthName")["Sales"].sum().reindex(MONTH_ORDER)
best_m         = monthly_total.idxmax()
best_d         = df.groupby("Weekday")["Sales"].sum().idxmax()
peak_h         = df.groupby("Hour")["Sales"].sum().idxmax()
with k1: st.metric("Best Month",   best_m, f"£{monthly_total[best_m]:,.0f}")
with k2: st.metric("Best Weekday", best_d)
with k3: st.metric("Peak Hour",    f"{peak_h}:00 – {peak_h+1}:00")
with k4: st.metric("Q4 Revenue",   f"£{df[df['Month'].isin([10,11,12])]['Sales'].sum():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# Heatmap: Month vs Weekday
section_header("🔥 Revenue Heatmap: Month × Weekday")
heat = df.groupby(["MonthName","Weekday"])["Sales"].sum().reset_index()
heat_pivot = heat.pivot(index="Weekday", columns="MonthName", values="Sales").reindex(
    index=DAY_ORDER, columns=MONTH_ORDER)

fig_heat = go.Figure(go.Heatmap(
    z=heat_pivot.values,
    x=heat_pivot.columns,
    y=heat_pivot.index,
    colorscale="Plasma",
    hoverongaps=False,
    hovertemplate="<b>%{y} × %{x}</b><br>Revenue: £%{z:,.0f}<extra></extra>",
))
fig_heat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#CBD5E1"), height=320,
    margin=dict(l=0,r=0,t=30,b=0),
    xaxis=dict(side="bottom"),
    coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"))
)
st.plotly_chart(fig_heat, use_container_width=True)

# Monthly + weekly
c1, c2 = st.columns(2)
with c1:
    section_header("📊 Average Monthly Revenue")
    avg_monthly = df.groupby(["MonthName","Month"])["Sales"].sum().reset_index()
    avg_monthly = avg_monthly.groupby(["MonthName","Month"])["Sales"].mean().reset_index().sort_values("Month")
    fig = go.Figure(go.Bar(
        x=avg_monthly["MonthName"], y=avg_monthly["Sales"],
        marker=dict(color=PALETTE[:12]),
        hovertemplate="<b>%{x}</b><br>Avg Revenue: £%{y:,.0f}<extra></extra>"
    ))
    fig = styled_chart(fig, 320)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("📆 Average Revenue by Day of Week")
    avg_day = df.groupby("Weekday")["Sales"].mean().reindex(DAY_ORDER).reset_index()
    fig2 = go.Figure(go.Bar(
        x=avg_day["Weekday"], y=avg_day["Sales"],
        marker=dict(color=SECONDARY),
        hovertemplate="<b>%{x}</b><br>Avg Revenue: £%{y:,.0f}<extra></extra>"
    ))
    fig2 = styled_chart(fig2, 320)
    st.plotly_chart(fig2, use_container_width=True)

# Hourly distribution
section_header("⏰ Revenue by Hour of Day")
hourly = df.groupby("Hour")["Sales"].sum().reset_index().sort_values("Hour")
hourly["Label"] = hourly["Hour"].astype(str).str.zfill(2) + ":00"
max_h = hourly["Sales"].max()
colors_h = [SUCCESS if s == max_h else PRIMARY for s in hourly["Sales"]]
fig3 = go.Figure(go.Bar(
    x=hourly["Label"], y=hourly["Sales"],
    marker=dict(color=colors_h),
    hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>"
))
fig3 = styled_chart(fig3, 300)
st.plotly_chart(fig3, use_container_width=True)

# Radar chart: monthly seasonality
section_header("🕸️ Seasonal Radar Chart")
radar = df.groupby(["MonthName","Month"])["Sales"].sum().reset_index().sort_values("Month")
fig4 = go.Figure(go.Scatterpolar(
    r=radar["Sales"].tolist() + [radar["Sales"].iloc[0]],
    theta=radar["MonthName"].tolist() + [radar["MonthName"].iloc[0]],
    fill="toself",
    line=dict(color=ACCENT, width=2),
    fillcolor="rgba(245,158,11,0.15)",
))
fig4.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    polar=dict(bgcolor="rgba(0,0,0,0)",
               angularaxis=dict(color="#94A3B8"),
               radialaxis=dict(color="#94A3B8", gridcolor="#2D2D44")),
    font=dict(color="#CBD5E1"), height=380, margin=dict(l=0,r=0,t=30,b=0)
)
st.plotly_chart(fig4, use_container_width=True)
