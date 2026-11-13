import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import butter, filtfilt, hilbert
from scipy.stats import kurtosis

def calculate_time_features(signal):
    if len(signal) == 0 or np.all(signal == 0):
        return {"rms": 0, "peak": 0, "crest_factor": 0, "kurtosis": 0}
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    cf = peak / rms if rms > 1e-6 else 0
    kurt = kurtosis(signal, fisher=False)
    return {"rms": rms, "peak": peak, "crest_factor": cf, "kurtosis": kurt}

def calculate_fft(signal, fs):
    n = len(signal)
    if n == 0: return np.array([]), np.array([])
    window = np.hanning(n)
    signal_w = signal * window
    yf = rfft(signal_w)
    xf = rfftfreq(n, 1 / fs)
    amplitude = 2.0 / n * np.abs(yf)
    amplitude = amplitude * 1.63
    return xf, amplitude

def calculate_envelope_spectrum(signal, fs, band=(1000, 5000)):
    n = len(signal)
    if n < 1024: return np.array([]), np.array([])
    nyq = 0.5 * fs
    low, high = band[0] / nyq, band[1] / nyq
    if high >= 1.0: high = 0.99
    b, a = butter(4, [low, high], btype='band')
    filtered = filtfilt(b, a, signal)
    analytic_signal = hilbert(filtered)
    amplitude_envelope = np.abs(analytic_signal)
    envelope_ac = amplitude_envelope - np.mean(amplitude_envelope)
    return calculate_fft(envelope_ac, fs)

def extract_harmonics(xf, amplitude, rpm, max_order=5):
    fr = rpm / 60.0
    harmonics = {}
    df = xf[1] - xf[0] if len(xf) > 1 else 1.0
    search_bins = int(2.0 / df) + 1
    for i in range(1, max_order + 1):
        target_f = i * fr
        idx = np.searchsorted(xf, target_f)
        if 0 < idx < len(xf):
            start = max(0, idx - search_bins)
            end = min(len(xf), idx + search_bins)
            harmonics[f"{i}x"] = np.max(amplitude[start:end])
        else:
            harmonics[f"{i}x"] = 0.0
    return harmonics
