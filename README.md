# 3GPP Rel-17 LEO NTN Diagnostic Engine

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ntn-rel17-diagnostic-engine.streamlit.app/)

## Overview
This project is an interactive Layer 1/L2 telemetry diagnostic tool designed for Non-Terrestrial Network (NTN) integration. It bridges the gap between Layer 3 RRC broadcast parameters (SIB19) and physical layer performance metrics, allowing RF optimization teams to predict and troubleshoot cell outages in high-speed LEO environments.

## Core Capabilities
* **Protocol Parsing:** Ingests post-parsed ASN.1 JSON payloads to extract Rel-17 ephemeris data, Common Timing Advance (TA), and K_offset variables.
* **Dynamic Simulation:** Features a real-time simulation engine to stress-test the network by overriding SIB19 `t-Service` and `K_offset` parameters, demonstrating the physical boundaries of the satellite link budget.
* **Automated Root Cause Analysis:** An embedded logic engine that automatically flags Mass IoT RACH Storms, Atmospheric Rain Fade (Ka-band), and imminent handover failures based on KPI thresholds.

## Tech Stack
* **Language:** Python (Pandas, NumPy)
* **Frontend:** Streamlit, Plotly (Dual-Axis interactive visualization)

## How to Run Locally
1. Clone this repository.
2. Install requirements: `pip install pandas numpy streamlit plotly`
3. Generate the baseline telemetry: `python log_generator.py`
4. Launch the diagnostic dashboard: `streamlit run app.py`
