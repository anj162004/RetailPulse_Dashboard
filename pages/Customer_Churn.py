import streamlit as st
import pandas as pd
import joblib

from utils import (
    set_page_config,
    inject_css,
    page_header,
    section_header
)

# ------------------------------
# Page Configuration
# ------------------------------
set_page_config("Customer Churn Prediction", "👤")
inject_css()

page_header(
    "👤 Customer Churn Prediction",
    "Predict whether a customer is likely to churn using the RFM model."
)

# ------------------------------
# Load Model
# ------------------------------
model = joblib.load("models/churn_model.pkl")

st.markdown("### Enter Customer Information")

c1, c2, c3 = st.columns(3)

with c1:
    recency = st.number_input(
        "Recency",
        min_value=0,
        value=30,
        help="Days since last purchase"
    )

with c2:
    frequency = st.number_input(
        "Frequency",
        min_value=1,
        value=5,
        help="Number of purchases"
    )

with c3:
    monetary = st.number_input(
        "Monetary (£)",
        min_value=0.0,
        value=500.0,
        help="Total amount spent"
    )

st.markdown("---")

if st.button("🔍 Predict Churn", use_container_width=True):

    input_df = pd.DataFrame({
        "Recency":[recency],
        "Frequency":[frequency],
        "Monetary":[monetary]
    })

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    st.markdown("## Prediction Result")

    if prediction == 1:
        st.error("⚠️ Customer is likely to churn.")
    else:
        st.success("✅ Customer is likely to stay.")

    st.metric(
        "Probability of Churn",
        f"{probability*100:.2f}%"
    )

    st.markdown("---")

    if probability > 0.70:
        st.warning("""
### Business Recommendation

- Offer loyalty rewards
- Send personalized promotions
- Contact customer proactively
""")

    else:
        st.info("""
### Business Recommendation

- Continue regular engagement
- Recommend complementary products
- Maintain customer satisfaction
""")