import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Customer Behaviour", "🧠")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("🧠 Customer Behaviour Dashboard", "Buying patterns, RFM analysis and loyalty segments")

# Build customer metrics
cust = (df.groupby("Customer ID")
          .agg(OrderCount=("Invoice","nunique"),
               TotalSpend=("Sales","sum"),
               TotalQty=("Quantity","sum"),
               UniqueProducts=("StockCode","nunique"),
               LastDate=("InvoiceDate","max"),
               FirstDate=("InvoiceDate","min"))
          .reset_index())
cust["AvgOrderValue"] = cust["TotalSpend"] / cust["OrderCount"]
max_date = pd.to_datetime(df["InvoiceDate"]).max()
cust["Recency"] = (max_date - pd.to_datetime(cust["LastDate"])).dt.days
cust["Tenure"]  = (pd.to_datetime(cust["LastDate"]) - pd.to_datetime(cust["FirstDate"])).dt.days

# RFM scoring
cust["R_score"] = pd.qcut(cust["Recency"],   q=4, labels=[4,3,2,1]).astype(int)
cust["F_score"] = pd.qcut(cust["OrderCount"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
cust["M_score"] = pd.qcut(cust["TotalSpend"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
cust["RFM"]     = cust["R_score"].astype(str) + cust["F_score"].astype(str) + cust["M_score"].astype(str)
cust["RFM_Total"] = cust["R_score"] + cust["F_score"] + cust["M_score"]

def rfm_segment(row):
    if row["RFM_Total"] >= 10: return "Champions"
    elif row["RFM_Total"] >= 8: return "Loyal Customers"
    elif row["RFM_Total"] >= 6: return "Potential Loyalists"
    elif row["R_score"] >= 3:   return "Recent Customers"
    elif row["F_score"] >= 3:   return "At Risk"
    else:                       return "Lost"
cust["Segment"] = cust.apply(rfm_segment, axis=1)

# KPIs
k1,k2,k3,k4 = st.columns(4)
champions = cust[cust["Segment"] == "Champions"]
at_risk   = cust[cust["Segment"] == "At Risk"]
with k1: st.metric("Champions",       f"{len(champions):,}", f"£{champions['TotalSpend'].sum():,.0f} revenue")
with k2: st.metric("Loyal Customers", f"{len(cust[cust['Segment']=='Loyal Customers']):,}")
with k3: st.metric("At Risk",         f"{len(at_risk):,}", f"{len(at_risk)/len(cust)*100:.1f}%", delta_color="inverse")
with k4: st.metric("Avg Customer Tenure", f"{cust['Tenure'].mean():.0f} days")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    section_header("🥧 RFM Customer Segments")
    seg_counts = cust["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment","Count"]
    seg_colors = {"Champions":SUCCESS,"Loyal Customers":PRIMARY,"Potential Loyalists":SECONDARY,
                  "Recent Customers":ACCENT,"At Risk":DANGER,"Lost":"#6B7280"}
    fig = go.Figure(go.Pie(
        labels=seg_counts["Segment"], values=seg_counts["Count"],
        marker=dict(colors=[seg_colors.get(s, PRIMARY) for s in seg_counts["Segment"]]),
        hole=0.52,
    ))
    fig = styled_chart(fig, 350)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("💰 Revenue by Segment")
    seg_rev = cust.groupby("Segment")["TotalSpend"].sum().reset_index().sort_values("TotalSpend", ascending=False)
    fig2 = go.Figure(go.Bar(
        x=seg_rev["TotalSpend"], y=seg_rev["Segment"],
        orientation="h",
        marker=dict(color=[seg_colors.get(s, PRIMARY) for s in seg_rev["Segment"]]),
    ))
    fig2 = styled_chart(fig2, 350)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Recency vs Frequency scatter
section_header("🔍 Recency vs Frequency (RFM Scatter)")
fig3 = px.scatter(
    cust, x="Recency", y="OrderCount",
    color="Segment",
    size="TotalSpend",
    color_discrete_map=seg_colors,
    labels={"Recency":"Days Since Last Order","OrderCount":"# Orders"},
    size_max=25,
    opacity=0.7,
    hover_data={"Customer ID": True, "TotalSpend": ":.2f"},
)
fig3 = styled_chart(fig3, 400)
st.plotly_chart(fig3, use_container_width=True)

# Order frequency distribution
c3, c4 = st.columns(2)
with c3:
    section_header("📊 Order Frequency Distribution")
    cap = cust[cust["OrderCount"] <= cust["OrderCount"].quantile(0.95)]
    fig4 = go.Figure(go.Histogram(
        x=cap["OrderCount"], nbinsx=40,
        marker=dict(color=PRIMARY, line=dict(color="#0D0D1A", width=0.5)),
    ))
    fig4 = styled_chart(fig4, 280)
    fig4.update_layout(xaxis_title="Orders per Customer", yaxis_title="# Customers")
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    section_header("🕐 Tenure Distribution (days)")
    fig5 = go.Figure(go.Histogram(
        x=cust["Tenure"], nbinsx=40,
        marker=dict(color=ACCENT, line=dict(color="#0D0D1A", width=0.5)),
    ))
    fig5 = styled_chart(fig5, 280)
    fig5.update_layout(xaxis_title="Customer Tenure (days)", yaxis_title="# Customers")
    st.plotly_chart(fig5, use_container_width=True)
