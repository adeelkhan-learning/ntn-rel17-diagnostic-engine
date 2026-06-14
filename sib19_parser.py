import json

def parse_sib19_trace(file_path):
    """Reads a simulated SIB19 JSON trace and extracts critical NTN parameters."""
    print(f"Loading trace from: {file_path}...\n")
    
    with open(file_path, 'r') as f:
        data = json.load(f)

    try:
        # Navigate the JSON tree to the NTN configuration
        ntn_config = data['sib19-v1700']['ntn-Config-r17']
        
        # Extract the specific 3GPP Rel-17 parameters
        common_ta = ntn_config['ta-Info-r17']['ta-Common-r17']
        ta_drift = ntn_config['ta-Info-r17']['ta-CommonDrift-r17']
        k_offset = ntn_config['k-Offset-r17']
        t_service = ntn_config['t-Service-r17']
        
        # Output the results to the terminal
        print("--- 3GPP Rel-17 SIB19 Decode Successful ---")
        print(f"Common Timing Advance : {common_ta} ms")
        print(f"TA Drift Rate         : {ta_drift} us/s")
        print(f"Scheduling Offset (K) : {k_offset} slots")
        print(f"Time to Service Expiry: {t_service} seconds")
        
        if t_service < 300:
            print("\n>> WARNING: Low t-Service detected. Handover imminent. <<")
            
        return {
            "common_ta": common_ta,
            "ta_drift": ta_drift,
            "k_offset": k_offset,
            "t_service": t_service
        }
        
    except KeyError as e:
        print(f"Error parsing trace. Missing required 3GPP key: {e}")
        return None

if __name__ == "__main__":
    # When this script is run directly, test the parser on our sample file
    extracted_parameters = parse_sib19_trace('sample_sib19.json')