import numpy as np
import pandas as pd

def generate_demo_data(fs=25600, duration=2, rpm=1500, fault_type="misalignment"):
    """Reproducible demo data generator with specific fault patterns."""
    np.random.seed(20261113) # Magic seed from the report
    
    n_samples = int(fs * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    fr = rpm / 60.0
    
    # Base signal (normal control: 0.2*sin(1x) + 0.05*sin(2x) + noise)
    signal = 0.2 * np.sin(2 * np.pi * fr * t) + 0.05 * np.sin(2 * np.pi * 2 * fr * t)
    signal += np.random.normal(0, 0.1, n_samples)
    
    if fault_type == "misalignment":
        # misalign_h: 1*sin(1x) + 2*sin(2x)
        # misalign_a: 2*sin(1x) + 4*sin(2x)
        signal_h = signal + 1.0 * np.sin(2 * np.pi * fr * t) + 2.0 * np.sin(2 * np.pi * 2 * fr * t)
        signal_v = signal + 0.8 * np.sin(2 * np.pi * fr * t) + 1.5 * np.sin(2 * np.pi * 2 * fr * t)
        signal_a = signal + 2.0 * np.sin(2 * np.pi * fr * t) + 4.0 * np.sin(2 * np.pi * 2 * fr * t)
        
        df_vib = pd.DataFrame({
            "time_s": t,
            "pump_de_h": signal_h,
            "pump_de_v": signal_v,
            "pump_de_a": signal_a
        })
        
    elif fault_type == "bearings":
        # 100 Hz pulses with 4000 Hz resonance
        bpfo = 100.0
        
        # Create pulses
        pulses = np.zeros_like(t)
        pulse_indices = np.arange(0, n_samples, int(fs/bpfo))
        pulse_indices = pulse_indices[pulse_indices < n_samples]
        
        # Generate decaying resonance for each pulse
        resonance_freq = 4000.0
        decay_time = 0.0006
        
        signal_h = np.copy(signal)
        for idx in pulse_indices:
            # Add pulse response starting at idx
            remaining_samples = n_samples - idx
            t_decay = t[:remaining_samples]
            response = 8.0 * np.exp(-t_decay / decay_time) * np.sin(2 * np.pi * resonance_freq * t_decay)
            signal_h[idx:] += response
            
        df_vib = pd.DataFrame({
            "time_s": t,
            "pump_de_h": signal_h,
            "pump_de_v": signal * 0.8 + np.random.normal(0, 0.1, n_samples)
        })
        
    elif fault_type == "looseness":
        # loose_h: sum(2/k * sin(k*1x)) + 0.5*sin(0.5x)
        signal_h = np.copy(signal)
        signal_h += 0.5 * np.sin(2 * np.pi * (0.5 * fr) * t)
        
        for k in range(1, 9):
            signal_h += (2.0 / k) * np.sin(2 * np.pi * (k * fr) * t)
            
        df_vib = pd.DataFrame({
            "time_s": t,
            "pump_de_h": signal_h,
            "pump_de_v": signal_h * 0.5 + np.random.normal(0, 0.1, n_samples)
        })
    else:
        # Normal
        df_vib = pd.DataFrame({
            "time_s": t,
            "pump_de_h": signal,
            "pump_de_v": signal * 0.8 + np.random.normal(0, 0.1, n_samples)
        })
    
    # Slow operational data (1 Hz)
    t_slow = np.arange(0, duration, 1)
    df_op = pd.DataFrame({
        "timestamp": t_slow,
        "speed_rpm": np.linspace(rpm, rpm+1, len(t_slow)),
        "bearing_temp_c": np.linspace(45, 45.5, len(t_slow)),
        "motor_current_rms_a": np.random.normal(12.5, 0.1, len(t_slow))
    })
    
    meta = {
        "project_id": f"DEMO-{fault_type.upper()}",
        "machine_id": "PUMP-A-01",
        "nominal_rpm": rpm,
        "data_origin": "szimulált",
        "simulated_fault": fault_type
    }
    
    return df_vib, df_op, meta
