import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

def load_sib19_baselines(sib19_file):
    """Helper to safely load baselines from our parsed SIB19 structure."""
    try:
        with open(sib19_file, 'r') as f:
            data = json.load(f)
        ntn_config = data['sib19-v1700']['ntn-Config-r17']
        return {
            "base_rtt": ntn_config['ta-Info-r17']['ta-Common-r17'] * 2, # RTT = 2 * TA
            "k_offset": ntn_config['k-Offset-r17'],
            "t_service": ntn_config['t-Service-r17']
        }
    except Exception:
        # Fallback parameters if file missing
        return {"base_rtt": 50.8, "k_offset": 40, "t_service": 120}

def generate_ntn_telemetry():
    baselines = load_sib19_baselines('sample_sib19.json')
    print("--- Initializing NTN Log Generation Engine ---")
    print(f"Using SIB19 Baselines -> RTT: {baselines['base_rtt']}ms, K-offset: {baselines['k_offset']} slots\n")
    
    # Generate 180 entries (3 hours of telemetry at 1-minute intervals)
    base_time = datetime(2026, 6, 13, 12, 0, 0)
    records = []
    
    for i in range(180):
        current_time = base_time + timedelta(minutes=i)
        
        # Default Baseline Values (Normal Operation)
        # Add slight sinusoidal drift to simulate LEO movement relative to the ground terminal
        rtt = baselines['base_rtt'] + (2.5 * np.sin(i / 15.0))
        sinr = 14.5 + np.random.normal(0, 0.5)
        rach_attempts = np.random.randint(40, 60)
        rach_failures = np.random.randint(0, 3)
        bler = round(max(0.01, 0.02 + np.random.normal(0, 0.005)), 3)
        
        # Scenario 1: Mass IoT RACH Storm (Minutes 40 to 80)
        if 40 <= i <= 80:
            # Massive spike in registration attempts causes preamble collisions
            rach_attempts = np.random.randint(800, 1200)
            rach_failures = int(rach_attempts * np.random.uniform(0.65, 0.85))
            sinr -= 1.5 # Minor degradation due to increased noise floor
            
        # Scenario 2: Ka-Band Rain Fade & Handover Drop (Minutes 120 to 160)
        elif 120 <= i <= 160:
            # Simulate heavy atmospheric attenuation
            attenuation = (i - 120) * 0.4 # Gradually worsening attenuation
            sinr = max(-3.0, sinr - attenuation)
            bler = min(1.0, bler + (attenuation * 0.08))
            
            # As connection drops, RACH failures increase
            if sinr < 0:
                rach_failures = int(rach_attempts * 0.95)
        
        # Calculate resulting KPI with the fixed variable name
        rach_success_rate = round(((rach_attempts - rach_failures) / rach_attempts) * 100, 2) if rach_attempts > 0 else 100.0
        
        records.append({
            "Timestamp": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "Satellite_Cell_ID": "Sat_Cell_LEO_09",
            "Beam_ID": "Beam_03",
            "RTT_ms": round(rtt, 2),
            "SINR_dB": round(sinr, 2),
            "K_Offset_Slots": baselines['k_offset'],
            "RACH_Attempts": rach_attempts,
            "RACH_Failures": rach_failures,
            "RACH_Success_Rate_%": rach_success_rate,
            "BLER": round(bler, 3)
        })
        
    df = pd.DataFrame(records)
    output_file = "ntn_performance_logs.csv"
    df.to_csv(output_file, index=False)
    print(f"Success: Telemetry engine complete. Generated {len(df)} lines of raw data.")
    print(f"Log file saved safely as: '{output_file}'")

if __name__ == "__main__":
    generate_ntn_telemetry()