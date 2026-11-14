import numpy as np
import pandas as pd
from pumpdiag import signal_processing, diagnostics

def test_time_and_sampling():
    # Generate 25Hz sine with 1000Hz sampling
    fs = 1000.0
    t = np.linspace(0, 1, int(fs), endpoint=False)
    sig = np.sin(2 * np.pi * 25 * t)
    
    # Check time axis logic
    ok, msg, actual_fs = signal_processing.check_time_axis(t)
    assert ok
    assert np.isclose(actual_fs, 1000.0)
    
    # Check FFT frequency matching
    xf, yf = signal_processing.calculate_fft(sig, actual_fs)
    peak_freq = xf[np.argmax(yf)]
    assert np.isclose(peak_freq, 25.0)

def test_amplitude_scaling():
    # 25Hz sine with 2.0 amplitude, 1000Hz sampling
    fs = 1000.0
    t = np.linspace(0, 10, int(fs*10), endpoint=False)
    sig = 2.0 * np.sin(2 * np.pi * 25 * t)
    
    ok, msg, sig_ac = signal_processing.validate_signal(sig, fs)
    xf, yf = signal_processing.calculate_fft(sig_ac, fs)
    
    peak_amp = np.max(yf)
    # The error in the original was it gave ~1.63 instead of 2.0
    # Tolerance to 1% as requested
    assert np.isclose(peak_amp, 2.0, rtol=0.01), f"Expected 2.0, got {peak_amp}"

def test_data_quality_gate():
    # Test flat signal
    flat = np.ones(2000) * 5.0
    t = np.linspace(0, 1, 2000)
    ok, msg, fs = signal_processing.check_time_axis(t)
    sig_ok, sig_msg, processed = signal_processing.validate_signal(flat, fs)
    assert not sig_ok
    assert "állandó vagy zérus" in sig_msg

    # Test short signal
    short = np.random.randn(100)
    sig_ok, sig_msg, processed = signal_processing.validate_signal(short, 1000)
    assert not sig_ok
    assert "túl rövid" in sig_msg

def test_diagnostics_rules():
    # Single shock vs periodic
    # The rule was fixed to require high kurtosis AND envelope peaks
    # We will simulate the outputs of the signal processing
    
    features_shock = {'kurtosis': 15.0} # high kurtosis
    harmonics = {'1x': 0.1, '2x': 0.1}
    env_shock = {'has_peaks': False} # No repeating peaks in envelope
    
    primary, res = diagnostics.evaluate_diagnostics(features_shock, harmonics, 1500, env_shock, {})
    
    # Should NOT be supported as a bearing fault without envelope peaks (score drops below 5)
    bearing_res = next(r for r in res if r['id'] == 'bearing_fault')
    assert bearing_res['status'] == 'nem támogatott'

def test_foundation_rule():
    features = {'rms': 1.0}
    harmonics = {'1x': 3.0} # High 1x
    metadata_no_loc = {'measurement_location': 'ismeretlen'}
    metadata_loc = {'measurement_location': 'gépláb'}
    
    # Without location, should not be fully supported, but missing data noted
    primary, res = diagnostics.evaluate_diagnostics(features, harmonics, 1500, None, metadata_no_loc)
    found_res = next(r for r in res if r['id'] == 'foundation')
    assert found_res['status'] == 'nem támogatott' # Score 3
    assert len(found_res['missing']) > 0
    
    # With correct location, it should be supported
    primary, res = diagnostics.evaluate_diagnostics(features, harmonics, 1500, None, metadata_loc)
    found_res = next(r for r in res if r['id'] == 'foundation')
    assert found_res['status'] == 'támogatott' # Score 6

if __name__ == '__main__':
    test_time_and_sampling()
    test_amplitude_scaling()
    test_data_quality_gate()
    test_diagnostics_rules()
    test_foundation_rule()
    print("All integration tests passed successfully.")
