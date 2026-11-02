import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PHT Incentive Simulator", page_icon="⚙️", layout="wide"
)

st.title("🏭 PHT Production Incentive Simulator")
st.markdown(
    "### Interactive 3-Pillar Gainsharing Model: Production (150h) • QC (13h) •"
    " Store (10h)"
)

# ==========================================
# SIDEBAR INTERACTIVE INPUTS
# ==========================================
st.sidebar.header("📊 Simulation Parameters")

units = st.sidebar.slider(
    "Monthly Radiators Produced", min_value=80, max_value=200, value=150, step=5
)
rate = st.sidebar.number_input(
    "Loaded Conversion Rate (RM/hr)", value=25.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.header("👥 Department Headcounts")
prod_hc = st.sidebar.number_input(
    "Production Headcount (Workers)", value=60, step=1
)
qc_hc = st.sidebar.number_input(
    "QC Headcount (Inspectors)", value=6, step=1
)
store_hc = st.sidebar.number_input("Store Headcount (Handlers)", value=5, step=1)

# ==========================================
# CALCULATIONS
# ==========================================
effective_rate = rate * 0.6  # 60% worker pool share

# 1. Production Floor (Std: 150h, Actual: 138.5h, Rework: 100h)
prod_saved = max(0.0, (units * 150.0 - units * 138.5) - 100)
prod_pool_m = prod_saved * effective_rate
prod_q_per_worker = (prod_pool_m * 3) / prod_hc if prod_hc > 0 else 0

# 2. Quality Control (Std: 13h, Actual: 11.1h with 1.20 mult)
qc_saved = max(0.0, (units * 13.0 - units * 11.1)) * 1.20
qc_pool_m = qc_saved * effective_rate
qc_q_per_worker = (qc_pool_m * 3) / qc_hc if qc_hc > 0 else 0

# 3. Store Logistics (Std: 10h, Actual: 10.7h)
store_saved = max(0.0, units * 10.0 - units * 10.7)
store_pool_m = max(0.0, store_saved) * effective_rate
store_q_per_worker = (store_pool_m * 3) / store_hc if store_hc > 0 else 0

total_quarterly_pool = (prod_pool_m + qc_pool_m + store_pool_m) * 3
total_annual_gain = (
    (prod_saved + qc_saved + store_saved) * rate * 0.4
) * 12

# ==========================================
# TOP EXECUTIVE METRICS
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Monthly Output", f"{units} Units")
col2.metric(
    "Total Quarterly Worker Pool", f"RM {total_quarterly_pool:,.2f}"
)
col3.metric("Annual Company Gain", f"RM {total_annual_gain:,.2f}")

st.markdown("---")
st.subheader("📊 Departmental Performance & Payout Breakdown (Quarterly)")

summary_df = pd.DataFrame({
    "Department": [
        f"Production Floor ({prod_hc} workers)",
        f"Quality Control ({qc_hc} inspectors)",
        f"Store Logistics ({store_hc} handlers)",
    ],
    "Audited Benchmark": ["150.0h / unit", "13.0h / unit", "10.0h / unit"],
    "Net Saved Hours (Monthly)": [
        f"{prod_saved:,.1f} hrs",
        f"{qc_saved:,.1f} hrs",
        f"{store_saved:,.1f} hrs",
    ],
    "Quarterly Pool (Dept)": [
        f"RM {prod_pool_m * 3:,.2f}",
        f"RM {qc_pool_m * 3:,.2f}",
        f"RM {store_pool_m * 3:,.2f}",
    ],
    "Quarterly Payout / Worker": [
        f"RM {prod_q_per_worker:,.2f}",
        f"RM {qc_q_per_worker:,.2f}",
        f"RM {store_q_per_worker:,.2f}",
    ],
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)
