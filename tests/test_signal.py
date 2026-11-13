import numpy as np
from pumpdiag import signal_processing

def test_features():
    sig = 2.0 * np.sin(2 * np.pi * 1.0 * np.linspace(0, 1, 1000))
    f = signal_processing.calculate_time_features(sig)
    assert np.isclose(f['peak'], 2.0, atol=0.01)

def test_fft():
    sig = np.sin(2 * np.pi * 50 * np.linspace(0, 1, 1000))
    xf, yf = signal_processing.calculate_fft(sig, 1000)
    assert np.isclose(xf[np.argmax(yf)], 50.0, atol=1.0)
