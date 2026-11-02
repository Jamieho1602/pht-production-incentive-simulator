import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PHT Incentive Simulator", page_icon="⚙️", layout="wide"
)

st.title("🏭 PHT Production Incentive Simulator")
st.markdown(
    "### Executive Gainsharing Dashboard: Plant-Wide Totals & Departmental"
    " Breakdown"
)

# ==========================================
# SIDEBAR PARAMETERS & ACTUALS INPUTS
# ==========================================
st.sidebar.header("📊 Production Volume")
units = st.sidebar.slider(
    "Monthly Radiators Produced", min_value=80, max_value=200, value=150, step=5
)
rate = st.sidebar.number_input(
    "Loaded Conversion Rate (RM/hr)", value=25.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Actual Hours vs Benchmarks")
prod_actual_h = st.sidebar.slider(
    "Production Actual Hrs/Unit (Std: 150h)", 130.0, 165.0, 138.5, 0.5
)
qc_actual_h = st.sidebar.slider(
    "QC Actual Hrs/Unit (Std: 13.0h)", 10.0, 18.0, 11.1, 0.1
)
store_actual_h = st.sidebar.slider(
    "Store Actual Hrs/Unit (Std: 10.0h)", 8.0, 16.0, 10.7, 0.1
)

st.sidebar.markdown("---")
st.sidebar.header("👥 Headcounts")
prod_hc = st.sidebar.number_input("Production Headcount", value=60)
qc_hc = st.sidebar.number_input("QC Headcount", value=6)
store_hc = st.sidebar.number_input("Store Headcount", value=5)

# ==========================================
# CALCULATIONS (INDEPENDENT TEAM POOLS)
# ==========================================
effective_rate = rate * 0.6  # 60% worker share

# 1. Production Floor
prod_saved = max(
    0.0, (units * 150.0 - units * prod_actual_h) - 100
)  # 100h rework deduction
prod_pool_m = prod_saved * effective_rate
prod_q_per_worker = (prod_pool_m * 3) / prod_hc if prod_hc > 0 else 0

# 2. Quality Control
qc_saved = max(0.0, units * 13.0 - units * qc_actual_h) * 1.20
qc_pool_m = qc_saved * effective_rate
qc_q_per_worker = (qc_pool_m * 3) / qc_hc if qc_hc > 0 else 0

# 3. Store Logistics
store_saved = max(0.0, units * 10.0 - units * store_actual_h)
store_pool_m = store_saved * effective_rate
store_q_per_worker = (store_pool_m * 3) / store_hc if store_hc > 0 else 0

# --- TIER 1: PLANT-WIDE TOTALS ---
total_monthly_saved = prod_saved + qc_saved + store_saved
total_quarterly_worker_pool = (
    prod_pool_m + qc_pool_m + store_pool_m
) * 3
total_annual_labour_savings = (total_monthly_saved * rate * 0.4) * 12

# ==========================================
# TOP TIER: EXECUTIVE PLANT-WIDE METRICS
# ==========================================
st.markdown("### 🌐 Tier 1: Plant-Wide Financial Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Output", f"{units} Units")
col2.metric(
    "Total Monthly Saved Hours", f"{total_monthly_saved:,.1f} hrs"
)
col3.metric(
    "Total Quarterly Worker Pool",
    f"RM {total_quarterly_worker_pool:,.2f}",
)
col4.metric(
    "Annual Labour Cost Savings", f"RM {total_annual_labour_savings:,.2f}"
)

st.markdown("---")

# ==========================================
# BOTTOM TIER: INDIVIDUAL DEPARTMENT BREAKDOWN
# ==========================================
st.markdown("### 📊 Tier 2: Individual Departmental Breakdown")

summary_df = pd.DataFrame({
    "Department": [
        f"Production Floor ({prod_hc} workers)",
        f"Quality Control ({qc_hc} inspectors)",
        f"Store Logistics ({store_hc} handlers)",
    ],
    "Benchmark vs Actual": [
        f"150.0h vs {prod_actual_h}h",
        f"13.0h vs {qc_actual_h}h",
        f"10.0h vs {store_actual_h}h",
    ],
    "Net Saved Hours (Mth)": [
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
    "Performance Status": [
        ("✅ Achieved" if prod_saved > 0 else "❌ Missed Target"),
        ("✅ Achieved" if qc_saved > 0 else "❌ Missed Target"),
        ("✅ Achieved" if store_saved > 0 else "❌ Missed Target"),
    ],
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)
