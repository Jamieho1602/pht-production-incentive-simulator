import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="PHT Incentive Simulator", layout="wide")

st.title("🏭 PHT Production Incentive Simulator")
st.markdown("### Quarterly Gainsharing & Bonus Replacement Model")

# Sidebar inputs
st.sidebar.header("Settings")
units = st.sidebar.slider("Monthly Radiators Produced", 80, 200, 125, 5)
rate = st.sidebar.number_input("Loaded Conversion Rate (RM/hr)", value=25.0)

# Calculations
prod_saved = max(0.0, (units * 150.0 - units * 138.5) - 100)
pool_monthly = prod_saved * (rate * 0.6)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Monthly Output", f"{units} Units")
col2.metric("Quarterly Worker Pool", f"RM {pool_monthly * 3:,.2f}")
col3.metric("Annual Company Gain", f"RM {(prod_saved * rate * 0.4) * 12:,.2f}")

st.success("App is running successfully!")
st.dataframe(pd.DataFrame({
    "Metric": ["Units Produced", "Net Saved Hours", "Quarterly Bonus Pool"],
    "Value": [units, prod_saved, f"RM {pool_monthly * 3:,.2f}"]
}))
