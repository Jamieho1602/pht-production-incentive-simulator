import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PHT Tiered Incentive Simulator", page_icon="⚙️", layout="wide"
)

st.title("🏭 PHT Tiered Production Incentive Simulator")
st.markdown(
    "### Multi-Tier Performance Matrix: Production, QC, Store + Safety &"
    " Attendance"
)

# ==========================================
# SIDEBAR PARAMETERS & INPUTS
# ==========================================
st.sidebar.header("📊 Production Volume & Rates")
units = st.sidebar.slider(
    "Monthly Radiators Produced", min_value=80, max_value=200, value=150, step=5
)
rate = st.sidebar.number_input(
    "Loaded Conversion Rate (RM/hr)", value=25.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Actual Hours per Unit")
prod_actual_h = st.sidebar.slider(
    "Production Actual (Target: 150h)", 130.0, 170.0, 145.0, 0.5
)
qc_actual_h = st.sidebar.slider(
    "QC Actual (Target: 13.0h)", 10.0, 16.0, 12.5, 0.1
)
store_actual_h = st.sidebar.slider(
    "Store Actual (Target: 10.0h)", 8.0, 13.0, 9.5, 0.1
)

st.sidebar.markdown("---")
st.sidebar.header("🛡️ Safety & Attendance Compliance")
safety_achieved = st.sidebar.checkbox(
    "Zero Safety Incidents (Plant-wide)", value=True
)
attendance_rate = st.sidebar.slider(
    "Plant Attendance Rate (%)", 85.0, 100.0, 98.0, 0.5
)

st.sidebar.markdown("---")
st.sidebar.header("👥 Headcounts")
prod_hc = st.sidebar.number_input("Production Headcount", value=60)
qc_hc = st.sidebar.number_input("QC Headcount", value=6)
store_hc = st.sidebar.number_input("Store Headcount", value=5)


# ==========================================
# TIERED PAYOUT LOGIC FUNCTIONS
# ==========================================
def calc_production_tier(actual):
  if actual < 140.0:
    return "Tier 1: <140h (Highest)", 1.25, "✅ Tier 1"
  elif 140.0 <= actual <= 149.9:
    return "Tier 2: 140-149.9h (Higher)", 1.00, "✅ Tier 2"
  elif actual == 150.0:
    return "Tier 3: Exactly 150h (Baseline)", 0.50, "✅ Baseline"
  elif 150.1 <= actual <= 160.0:
    return "Tier 4: 150.1-160h (Lesser)", 0.25, "⚠️ Tier 4"
  else:
    return "Tier 5: >160h (No Reward)", 0.0, "❌ No Reward"


def calc_qc_tier(actual):
  if actual < 11.5:
    return "Tier 1: <11.5h (Highest)", 1.25, "✅ Tier 1"
  elif 11.5 <= actual <= 12.9:
    return "Tier 2: 11.5-12.9h (Higher)", 1.00, "✅ Tier 2"
  elif actual == 13.0:
    return "Tier 3: Exactly 13h (Baseline)", 0.50, "✅ Baseline"
  elif 13.1 <= actual <= 14.5:
    return "Tier 4: 13.1-14.5h (Lesser)", 0.25, "⚠️ Tier 4"
  else:
    return "Tier 5: >14.5h (No Reward)", 0.0, "❌ No Reward"


def calc_store_tier(actual):
  if actual < 9.0:
    return "Tier 1: <9.0h (Highest)", 1.25, "✅ Tier 1"
  elif 9.0 <= actual <= 9.9:
    return "Tier 2: 9.0-9.9h (Higher)", 1.00, "✅ Tier 2"
  elif actual == 10.0:
    return "Tier 3: Exactly 10h (Baseline)", 0.50, "✅ Baseline"
  elif 10.1 <= actual <= 11.5:
    return "Tier 4: 10.1-11.5h (Lesser)", 0.25, "⚠️ Tier 4"
  else:
    return "Tier 5: >11.5h (No Reward)", 0.0, "❌ No Reward"


# Get tiers and multipliers
prod_tier_name, prod_mult, prod_status = calc_production_tier(prod_actual_h)
qc_tier_name, qc_mult, qc_status = calc_qc_tier(qc_actual_h)
store_tier_name, store_mult, store_status = calc_store_tier(store_actual_h)

# Base hourly gainsharing value modified by tier weights
effective_rate = rate * 0.6
prod_pool_m = (
    max(0.0, (150.0 - prod_actual_h) * units) * effective_rate * prod_mult
    if prod_mult > 0
    else (15.0 * units * effective_rate * 0.5 if prod_mult == 0.5 else 0)
)
# Fixed baseline modifier for exact target hits
if prod_actual_h == 150.0:
  prod_pool_m = 15.0 * units * effective_rate * 0.5  # Baseline reward pool

qc_pool_m = (
    max(0.0, (13.0 - qc_actual_h) * units) * effective_rate * qc_mult
)
if qc_actual_h == 13.0:
  qc_pool_m = 3.0 * units * effective_rate * 0.5

store_pool_m = (
    max(0.0, (10.0 - store_actual_h) * units) * effective_rate * store_mult
)
if store_actual_h == 10.0:
  store_pool_m = 2.0 * units * effective_rate * 0.5

# Safety & Attendance Monthly Bonus Pool (e.g., RM 50 per worker if targets met)
safety_bonus_total = (
    (prod_hc + qc_hc + store_hc) * 50.0 if safety_achieved else 0.0
)
attendance_bonus_total = (
    (prod_hc + qc_hc + store_hc) * 30.0 if attendance_rate >= 95.0 else 0.0
)

# Quarterly Totals
total_quarterly_worker_pool = (
    (prod_pool_m + qc_pool_m + store_pool_m) * 3
) + ((safety_bonus_total + attendance_bonus_total) * 3)
total_quarterly_prod_worker = (
    (prod_pool_m * 3) + (safety_bonus_total + attendance_bonus_total) * 3
) / prod_hc
total_quarterly_qc_worker = (
    (qc_pool_m * 3) + (safety_bonus_total + attendance_bonus_total) * 3
) / qc_hc
total_quarterly_store_worker = (
    (store_pool_m * 3) + (safety_bonus_total + attendance_bonus_total) * 3
) / store_hc

# ==========================================
# DASHBOARD DISPLAY
# ==========================================
st.markdown("### 🌐 Tier 1: Plant-Wide Financial Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Output", f"{units} Units")
col2.metric("Safety Status", "Achieved ✅" if safety_achieved else "Missed ❌")
col3.metric("Attendance Rate", f"{attendance_rate}%")
col4.metric(
    "Total Quarterly Worker Pool", f"RM {total_quarterly_worker_pool:,.2f}"
)

st.markdown("---")
st.markdown("### 📊 Tier 2: Departmental Tier & Payout Breakdown")

summary_df = pd.DataFrame({
    "Department": [
        f"Production Floor ({prod_hc} workers)",
        f"Quality Control ({qc_hc} inspectors)",
        f"Store Logistics ({store_hc} handlers)",
    ],
    "Performance Tier": [prod_tier_name, qc_tier_name, store_tier_name],
    "Actual vs Target": [
        f"{prod_actual_h}h vs 150h",
        f"{qc_actual_h}h vs 13h",
        f"{store_actual_h}h vs 10h",
    ],
    "Quarterly Payout / Worker (Incl. Safety/Attendance)": [
        f"RM {total_quarterly_prod_worker:,.2f}",
        f"RM {total_quarterly_qc_worker:,.2f}",
        f"RM {total_quarterly_store_worker:,.2f}",
    ],
    "Status": [prod_status, qc_status, store_status],
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)
