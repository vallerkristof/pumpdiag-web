import numpy as np
import pandas as pd

def generate_demo_data(fs=25600, duration=10, rpm=1480, fault_type="misalignment"):
    np.random.seed(42)
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    fr = rpm / 60.0
    signal = 0.2 * np.sin(2 * np.pi * fr * t) + np.random.normal(0, 0.5, len(t))
    
    if fault_type == "misalignment":
        signal += 2.5 * np.sin(2 * np.pi * fr * t)
        signal += 1.5 * np.sin(2 * np.pi * 2 * fr * t)
    elif fault_type == "bearings":
        bpfo = 3.14 * fr
        pulses = np.zeros_like(t)
        pulse_indices = np.arange(0, len(t), int(fs/bpfo))
        pulse_indices = pulse_indices[pulse_indices < len(t)]
        pulses[pulse_indices] = 10.0
        from scipy.signal import butter, filtfilt
        b, a = butter(2, [2000/(fs/2), 4000/(fs/2)], btype='band')
        signal += filtfilt(b, a, pulses) * 3.0
    
    df_vib = pd.DataFrame({"time_s": t, "pump_de_h": signal, "pump_de_v": signal * 0.6 + np.random.normal(0, 0.2, len(t))})
    
    t_slow = np.arange(0, duration, 1)
    df_op = pd.DataFrame({
        "timestamp": t_slow,
        "speed_rpm": np.linspace(rpm, rpm+5, len(t_slow)),
        "bearing_temp_c": np.linspace(45, 46.5, len(t_slow)),
        "motor_current_rms_a": np.random.normal(12.5, 0.1, len(t_slow))
    })
    meta = {"project_id": "DEMO-001", "machine_id": "PUMP-A-01", "nominal_rpm": rpm, "data_origin": "szimulált"}
    return df_vib, df_op, meta
