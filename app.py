import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PHT Incentive Simulator", layout="wide")

st.title("🏭 PHT Production Incentive Simulator")
st.markdown(
    "### Comprehensive Model: Production (150h) • QC (13h) • Store (10h)"
)

# Sidebar inputs
st.sidebar.header("📊 Settings")
units = st.sidebar.slider(
    "Monthly Radiators Produced", min_value=80, max_value=200, value=125, step=5
)
rate = st.sidebar.number_input(
    "Loaded Conversion Rate (RM/hr)", value=25.0, step=1.0
)

# Pillar Calculations
# 1. Production Floor (Std: 150h, Actual ~138.5h, 100h rework deduction)
prod_saved = max(0.0, (units * 150.0 - units * 138.5) - 100)
prod_pool = prod_saved * (rate * 0.6)

# 2. Quality Control (Std: 13h, Actual ~11.1h)
qc_saved = max(0.0, (units * 13.0 - units * 11.1)) * 1.20
qc_pool = qc_saved * (rate * 0.6)

# 3. Store Logistics (Std: 10h, Actual ~10.7h)
store_saved = max(0.0, (units * 10.0 - units * 10.7))
store_pool = max(0.0, store_saved) * (rate * 0.6)

total_quarterly_pool = (prod_pool + qc_pool + store_pool) * 3
total_annual_gain = (
    (prod_saved + qc_saved + store_saved) * rate * 0.4
) * 12

# Top Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Monthly Output", f"{units} Units")
col2.metric(
    "Total Quarterly Worker Pool", f"RM {total_quarterly_pool:,.2f}"
)
col3.metric("Annual Company Gain", f"RM {total_annual_gain:,.2f}")

st.markdown("---")
st.subheader("📊 Departmental Breakdown (Quarterly)")

summary_df = pd.DataFrame({
    "Department": [
        "Production Floor (60 workers)",
        "Quality Control (6 inspectors)",
        "Store Logistics (5 handlers)",
    ],
    "Audited Benchmark": ["150.0h / unit", "13.0h / unit", "10.0h / unit"],
    "Net Saved Hours (Monthly)": [
        f"{prod_saved:,.1f} hrs",
        f"{qc_saved:,.1f} hrs",
        f"{store_saved:,.1f} hrs",
    ],
    "Quarterly Payout Pool": [
        f"RM {prod_pool * 3:,.2f}",
        f"RM {qc_pool * 3:,.2f}",
        f"RM {store_pool * 3:,.2f}",
    ],
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)
