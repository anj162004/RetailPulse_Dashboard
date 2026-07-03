import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Region/Country Sales", "🌍")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("🌍 Region / Country Sales Dashboard", "Geographic revenue distribution and market performance")

country = (df.groupby("Country")
             .agg(Revenue=("Sales","sum"),
                  Orders=("Invoice","nunique"),
                  Customers=("Customer ID","nunique"),
                  Qty=("Quantity","sum"))
             .reset_index()
             .sort_values("Revenue", ascending=False))
country["AOV"] = country["Revenue"] / country["Orders"]

# KPIs
k1,k2,k3,k4 = st.columns(4)
with k1: st.metric("Countries", f"{len(country):,}")
with k2: st.metric("UK Revenue Share", f"{country[country['Country']=='United Kingdom']['Revenue'].sum()/country['Revenue'].sum()*100:.1f}%")
with k3: st.metric("Intl Revenue", f"£{country[country['Country']!='United Kingdom']['Revenue'].sum():,.0f}")
with k4:
    top_intl = country[country["Country"] != "United Kingdom"].iloc[0]
    st.metric("Top Intl Market", top_intl["Country"], f"£{top_intl['Revenue']:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# Choropleth world map
section_header("🗺️ Revenue World Map")
fig_map = px.choropleth(
    country,
    locations="Country",
    locationmode="country names",
    color="Revenue",
    color_continuous_scale="Viridis",
    hover_data={"Orders": True, "Customers": True, "AOV": ":.2f"},
    labels={"Revenue":"Revenue (£)"},
)
fig_map.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False,
             showcoastlines=True, coastlinecolor="#2D2D44",
             showland=True, landcolor="#1E1E2E",
             showocean=True, oceancolor="#0D0D1A",
             showlakes=False,),
    margin=dict(l=0,r=0,t=0,b=0),
    coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"), title=dict(text="Revenue", font=dict(color="#94A3B8"))),
    height=420,
    font=dict(color="#CBD5E1"),
)
st.plotly_chart(fig_map, use_container_width=True)

# Bar charts
c1, c2 = st.columns(2)
with c1:
    section_header("📊 Revenue by Country (Top 15)")
    top15 = country.head(15).copy()
    fig = go.Figure(go.Bar(
        x=top15["Revenue"], y=top15["Country"],
        orientation="h",
        marker=dict(color=PALETTE[:15]),
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>"
    ))
    fig = styled_chart(fig, 420)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("💰 Avg Order Value by Country (excl. UK, Top 15)")
    intl = country[country["Country"] != "United Kingdom"].head(15).sort_values("AOV", ascending=False)
    fig2 = go.Figure(go.Bar(
        x=intl["AOV"], y=intl["Country"],
        orientation="h",
        marker=dict(color=ACCENT),
        hovertemplate="<b>%{y}</b><br>AOV: £%{x:,.2f}<extra></extra>"
    ))
    fig2 = styled_chart(fig2, 420)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Orders + Customers by country
c3, c4 = st.columns(2)
with c3:
    section_header("🛒 Orders by Country (Top 10)")
    top10o = country.sort_values("Orders", ascending=False).head(10)
    fig3 = go.Figure(go.Bar(
        x=top10o["Country"], y=top10o["Orders"],
        marker=dict(color=SECONDARY),
    ))
    fig3 = styled_chart(fig3, 300)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    section_header("👥 Customers by Country (Top 10)")
    top10c = country.sort_values("Customers", ascending=False).head(10)
    fig4 = go.Figure(go.Bar(
        x=top10c["Country"], y=top10c["Customers"],
        marker=dict(color=SUCCESS),
    ))
    fig4 = styled_chart(fig4, 300)
    st.plotly_chart(fig4, use_container_width=True)

# Table
section_header("📋 Country Summary Table")
display = country.copy()
display["Revenue"]   = display["Revenue"].map("£{:,.0f}".format)
display["AOV"]       = display["AOV"].map("£{:,.2f}".format)
display["Orders"]    = display["Orders"].map("{:,}".format)
display["Customers"] = display["Customers"].map("{:,}".format)
display["Qty"]       = display["Qty"].map("{:,}".format)
display.columns      = ["Country","Revenue","Orders","Customers","Qty Sold","Avg Order £"]
st.dataframe(display.reset_index(drop=True), use_container_width=True, height=350)
