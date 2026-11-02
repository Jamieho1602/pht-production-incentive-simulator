import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PHT Incentive Simulator", page_icon="⚙️", layout="wide"
)

st.title("🏭 PHT Tiered Production Incentive Simulator")
st.markdown("### Multi-Tier Model with Separate Safety & Attendance Rewards")

# ==========================================
# SIDEBAR INPUTS
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
st.sidebar.header("🛡️ Safety & Attendance Rewards")
safety_achieved = st.sidebar.checkbox(
    "Zero Safety Incidents (Plant-wide)", value=True
)
safety_monthly_amt = st.sidebar.number_input(
    "Safety Monthly Reward / Worker (RM)", value=50.0, step=10.0
)

attendance_achieved = st.sidebar.checkbox(
    "Attendance Target Met (>=95%)", value=True
)
attendance_monthly_amt = st.sidebar.number_input(
    "Attendance Monthly Reward / Worker (RM)", value=30.0, step=10.0
)

st.sidebar.markdown("---")
st.sidebar.header("👥 Headcounts")
prod_hc = st.sidebar.number_input("Production Headcount", value=60)
qc_hc = st.sidebar.number_input("QC Headcount", value=6)
store_hc = st.sidebar.number_input("Store Headcount", value=5)


# ==========================================
# TIER LOGIC FUNCTIONS
# ==========================================
def get_prod_tier(h):
  if h < 140.0:
    return "Highest Reward (<140h)", 1.25, "✅ Tier 1"
  elif 140.0 <= h <= 149.9:
    return "Higher Reward (140-149.9h)", 1.00, "✅ Tier 2"
  elif h == 150.0:
    return "Baseline Reward (150h)", 0.50, "✅ Baseline"
  elif 150.1 <= h <= 160.0:
    return "Lesser Reward (150.1-160h)", 0.25, "⚠️ Tier 4"
  else:
    return "No Reward (>160h)", 0.00, "❌ No Reward"


def get_qc_tier(h):
  if h < 11.5:
    return "Highest Reward (<11.5h)", 1.25, "✅ Tier 1"
  elif 11.5 <= h <= 12.9:
    return "Higher Reward (11.5-12.9h)", 1.00, "✅ Tier 2"
  elif h == 13.0:
    return "Baseline Reward (13h)", 0.50, "✅ Baseline"
  elif 13.1 <= h <= 14.5:
    return "Lesser Reward (13.1-14.5h)", 0.25, "⚠️ Tier 4"
  else:
    return "No Reward (>14.5h)", 0.00, "❌ No Reward"


def get_store_tier(h):
  if h < 9.0:
    return "Highest Reward (<9h)", 1.25, "✅ Tier 1"
  elif 9.0 <= h <= 9.9:
    return "Higher Reward (9-9.9h)", 1.00, "✅ Tier 2"
  elif h == 10.0:
    return "Baseline Reward (10h)", 0.50, "✅ Baseline"
  elif 10.1 <= h <= 11.5:
    return "Lesser Reward (10.1-11.5h)", 0.25, "⚠️ Tier 4"
  else:
    return "No Reward (>11.5h)", 0.00, "❌ No Reward"


prod_tier, prod_mult, prod_status = get_prod_tier(prod_actual_h)
qc_tier, qc_mult, qc_status = get_qc_tier(qc_actual_h)
store_tier, store_mult, store_status = get_store_tier(store_actual_h)

# ==========================================
# CALCULATIONS
# ==========================================
eff_rate = rate * 0.6

# Gainsharing pools (Quarterly)
prod_gain_q = (
    max(0.0, (150.0 - prod_actual_h) * units) * eff_rate * prod_mult * 3
    if prod_mult > 0
    else 0
)
if prod_actual_h == 150.0:
  prod_gain_q = (15.0 * units * eff_rate * 0.5) * 3

qc_gain_q = (
    max(0.0, (13.0 - qc_actual_h) * units) * eff_rate * qc_mult * 3
    if qc_mult > 0
    else 0
)
if qc_actual_h == 13.0:
  qc_gain_q = (3.0 * units * eff_rate * 0.5) * 3

store_gain_q = (
    max(0.0, (10.0 - store_actual_h) * units) * eff_rate * store_mult * 3
    if store_mult > 0
    else 0
)
if store_actual_h == 10.0:
  store_gain_q = (2.0 * units * eff_rate * 0.5) * 3

# Per worker quarterly bonuses
prod_gain_per_worker = prod_gain_q / prod_hc if prod_hc > 0 else 0
qc_gain_per_worker = qc_gain_q / qc_hc if qc_hc > 0 else 0
store_gain_per_worker = store_gain_q / store_hc if store_hc > 0 else 0

safety_q_per_worker = safety_monthly_amt * 3 if safety_achieved else 0.0
attendance_q_per_worker = (
    attendance_monthly_amt * 3 if attendance_achieved else 0.0
)

prod_total_worker = (
    prod_gain_per_worker + safety_q_per_worker + attendance_q_per_worker
)
qc_total_worker = (
    qc_gain_per_worker + safety_q_per_worker + attendance_q_per_worker
)
store_total_worker = (
    store_gain_per_worker + safety_q_per_worker + attendance_q_per_worker
)

total_quarterly_pool = prod_gain_q + qc_gain_q + store_gain_q + (
    (safety_q_per_worker + attendance_q_per_worker)
    * (prod_hc + qc_hc + store_hc)
)

annual_labour_savings = (
    max(
        0.0,
        (150.0 - prod_actual_h) * units
        + (13.0 - qc_actual_h) * units
        + (10.0 - store_actual_h) * units,
    )
    * rate
    * 0.4
) * 12

# ==========================================
# DASHBOARD DISPLAY
# ==========================================
st.markdown("### 🌐 Plant-Wide Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Output", f"{units} Units")
c2.metric("Safety Status", "Achieved ✅" if safety_achieved else "Missed ❌")
c3.metric("Total Quarterly Worker Pool", f"RM {total_quarterly_pool:,.2f}")
c4.metric("Annual Labour Cost Savings", f"RM {annual_labour_savings:,.2f}")

st.markdown("---")
st.markdown("### 📊 Departmental Tier & Detailed Payout Breakdown (Quarterly)")

df = pd.DataFrame({
    "Department": [
        f"Production ({prod_hc} workers)",
        f"QC ({qc_hc} inspectors)",
        f"Store ({store_hc} handlers)",
    ],
    "Actual vs Target": [
        f"{prod_actual_h}h vs 150h",
        f"{qc_actual_h}h vs 13h",
        f"{store_actual_h}h vs 10h",
    ],
    "Performance Tier": [prod_tier, qc_tier, store_tier],
    "Gainsharing (RM)": [
        f"RM {prod_gain_per_worker:,.2f}",
        f"RM {qc_gain_per_worker:,.2f}",
        f"RM {store_gain_per_worker:,.2f}",
    ],
    "Safety Bonus (RM)": [
        f"RM {safety_q_per_worker:,.2f}",
        f"RM {safety_q_per_worker:,.2f}",
        f"RM {safety_q_per_worker:,.2f}",
    ],
    "Attendance Bonus (RM)": [
        f"RM {attendance_q_per_worker:,.2f}",
        f"RM {attendance_q_per_worker:,.2f}",
        f"RM {attendance_q_per_worker:,.2f}",
    ],
    "Total Payout / Worker": [
        f"RM {prod_total_worker:,.2f}",
        f"RM {qc_total_worker:,.2f}",
        f"RM {store_total_worker:,.2f}",
    ],
    "Status": [prod_status, qc_status, store_status],
})

st.dataframe(df, use_container_width=True, hide_index=True)
