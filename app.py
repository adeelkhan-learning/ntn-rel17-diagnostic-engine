import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as plotly_go
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(page_title="NTN Diagnostic Engine", layout="wide", page_icon="🛰️")
st.title("🛰️ LEO NTN Layer 1/2 Diagnostic Engine")
st.markdown("Advanced telemetry correlation and predictive anomaly detection for 3GPP Rel-17 architectures.")

# 2. Dynamic File Upload Handlers
st.sidebar.header("📂 Data Ingestion")
uploaded_sib19 = st.sidebar.file_uploader("Upload SIB19 Trace (.json)", type=["json"])
uploaded_csv = st.sidebar.file_uploader("Upload Telemetry Logs (.csv)", type=["csv"])

# Helper functions to load data (either from upload or fallback to local)
def load_sib19():
    if uploaded_sib19 is not None:
        data = json.load(uploaded_sib19)
        return data['sib19-v1700']['ntn-Config-r17']
    elif os.path.exists('sample_sib19.json'):
        with open('sample_sib19.json', 'r') as f:
            data = json.load(f)
        return data['sib19-v1700']['ntn-Config-r17']
    return None
   
def load_telemetry(file_obj):
    if file_obj is not None:
        df = pd.read_csv(file_obj)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    elif os.path.exists("ntn_performance_logs.csv"):
        df = pd.read_csv("ntn_performance_logs.csv")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    return None

base_sib19 = load_sib19()
telemetry_df = load_telemetry(uploaded_csv)

if telemetry_df is not None:
    # 3. Interactive Sidebar Controls & Simulation
    st.sidebar.divider()
    st.sidebar.header("🎛️ Network Simulation Controls")
    
    scenario_choice = st.sidebar.selectbox(
        "Isolate Telemetry Window:",
        options=["All Logs", "Mass IoT RACH Storm", "Ka-Band Rain Fade"]
    )
    
    st.sidebar.subheader("Live SIB19 Parameter Override")
    
    sim_k_offset = st.sidebar.slider(
        "Scheduling Offset (K_offset)", 
        min_value=10, max_value=100, value=base_sib19['k-Offset-r17'] if base_sib19 else 40, step=5,
        help="Simulates the scheduling loop delay. High values degrade RACH."
    )
    
    sim_t_service = st.sidebar.slider(
        "Time to Service Expiry (t-Service)", 
        min_value=0, max_value=600, value=base_sib19['t-Service-r17'] if base_sib19 else 120, step=10,
        help="Countdown to satellite beam handover."
    )

    # 4. Data Processing & Dynamic Simulation Math
    if scenario_choice == "Mass IoT RACH Storm":
        working_df = telemetry_df.iloc[40:81].copy()
    elif scenario_choice == "Ka-Band Rain Fade":
        working_df = telemetry_df.iloc[120:161].copy()
    else:
        working_df = telemetry_df.copy()

    if sim_k_offset > 50:
        penalty_factor = 50 / sim_k_offset
        working_df['RACH_Success_Rate_%'] = working_df['RACH_Success_Rate_%'] * penalty_factor
        
    if sim_t_service < 60:
        working_df['BLER'] = working_df['BLER'] + np.random.uniform(0.05, 0.15, len(working_df))
        working_df['BLER'] = working_df['BLER'].clip(upper=1.0) # Physical ceiling fix

    # 5. Top Level Protocol Status Card
    st.header("📡 Layer 3 Protocol Status")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Common TA Reference", f"{base_sib19['ta-Info-r17']['ta-Common-r17']} ms" if base_sib19 else "N/A")
    
    if sim_k_offset > 50:
        c2.metric("Active K_offset", f"{sim_k_offset} slots", "Latency Penalty Active", delta_color="inverse")
    else:
        c2.metric("Active K_offset", f"{sim_k_offset} slots", "Nominal", delta_color="normal")
        
    if sim_t_service < 60:
        c3.metric("t-Service Remaining", f"{sim_t_service} s", "⚠️ Handover Critical", delta_color="inverse")
    else:
        c3.metric("t-Service Remaining", f"{sim_t_service} s", "Stable", delta_color="normal")

    c4.metric("Window Avg SINR", f"{working_df['SINR_dB'].mean():.1f} dB")

    st.divider()

    # 6. Advanced Plotly Visualizations
    st.header("📈 L1/L2 Performance Correlation")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("RF Link Budget Status")
        fig_rf = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rf.add_trace(plotly_go.Scatter(x=working_df['Timestamp'], y=working_df['SINR_dB'], name="SINR (dB)", line=dict(color='#0055ff', width=2)), secondary_y=False)
        fig_rf.add_trace(plotly_go.Scatter(x=working_df['Timestamp'], y=working_df['BLER']*100, name="BLER (%)", fill='tozeroy', line=dict(color='#ff0000', width=1)), secondary_y=True)
        fig_rf.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=50), legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5))
        fig_rf.update_yaxes(title_text="SINR (dB)", secondary_y=False)
        fig_rf.update_yaxes(title_text="BLER (%)", secondary_y=True)
        st.plotly_chart(fig_rf, use_container_width=True)

    with chart_col2:
        st.subheader("Access Integrity (RACH)")
        fig_rach = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rach.add_trace(plotly_go.Bar(x=working_df['Timestamp'], y=working_df['RACH_Attempts'], name="Total RACH Attempts", marker_color='rgba(169, 169, 169, 0.5)'), secondary_y=False)
        fig_rach.add_trace(plotly_go.Scatter(x=working_df['Timestamp'], y=working_df['RACH_Success_Rate_%'], name="Success Rate (%)", line=dict(color='#00ff00', width=3)), secondary_y=True)
        fig_rach.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=50), legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5))
        fig_rach.update_yaxes(title_text="Attempts Count", secondary_y=False)
        fig_rach.update_yaxes(title_text="Success Rate (%)", secondary_y=True, range=[0, 105])
        st.plotly_chart(fig_rach, use_container_width=True)

    st.divider()

    # 7. Automated Diagnostic Engine
    st.header("🧠 Automated Root Cause Diagnostics")
    
    avg_sr = working_df['RACH_Success_Rate_%'].mean()
    max_bler = working_df['BLER'].max()
    min_sinr = working_df['SINR_dB'].min()
    
    if avg_sr < 80.0 and sim_k_offset > 50:
        st.error(f"**Anomaly Detected: Access Degradation.** \nRACH Success Rate dropped to {avg_sr:.1f}%. \n\n**Root Cause:** The active K_offset of {sim_k_offset} slots is causing massive preamble collisions due to extended propagation loop delays. \n**Recommendation:** Trigger immediate dynamic preamble pool expansion (Rel-17 feature).")
    elif avg_sr < 80.0:
        st.warning(f"**Anomaly Detected: Mass IoT Preamble Storm.** \nRACH Attempts spiked heavily against baseline capacity, dropping success rate to {avg_sr:.1f}%. \n\n**Recommendation:** Evaluate PRACH configuration index and verify CE level mapping.")
    elif max_bler > 0.10 and min_sinr < 2.0:
        st.error(f"**Anomaly Detected: Severe RF Degradation (Likely Atmospheric/Rain Fade).** \nSINR collapsed to {min_sinr:.1f} dB causing BLER to spike to {max_bler*100:.1f}%. \n\n**Recommendation:** Switch to lower MCS tables. If in Ka-Band, initiate handover to neighboring beam or verify Feeder Link gateway integrity.")
    elif sim_t_service < 60:
        st.warning("**Diagnostic Alert: Imminent Cell Outage.** \nt-Service timer is critical. Ensure UE has decoded SIB19 ephemeris for target cell to prevent L3 handover failure.")
    else:
        st.success("**Network Stable.** All core L1/L2 KPIs and Layer 3 protocol timers are operating within standard 3GPP thresholds.")

else:
    st.error("Could not populate dashboard. Please upload a 'ntn_performance_logs.csv' file or run the log generator.")