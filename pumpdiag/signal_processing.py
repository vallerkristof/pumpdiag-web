import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import butter, filtfilt, hilbert
from scipy.stats import kurtosis

def validate_signal(signal, fs):
    """Data quality gate for the signal."""
    if signal is None or len(signal) == 0:
        return False, "Üres adat.", signal
    
    if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
        # Handle NaN/Inf by raising an error or returning invalid status
        return False, "A jel nem numerikus (NaN vagy Inf) értékeket tartalmaz.", signal
    
    if len(signal) < 1024:
        return False, "A jel túl rövid az érdemi elemzéshez (minimum 1024 minta szükséges).", signal
    
    # Check for constant signal (variance is 0)
    if np.var(signal) < 1e-10:
        return False, "A jel állandó vagy zérus, nincs értékelhető rezgés.", signal
        
    # DC removal (Mean removal)
    signal_ac = signal - np.mean(signal)
    
    return True, "OK", signal_ac

def check_time_axis(time_array, expected_fs=None):
    """Validate the time axis and determine actual sampling frequency."""
    if time_array is None or len(time_array) < 2:
        return False, "Hiányzó vagy túl rövid időalap.", None
        
    if np.any(np.isnan(time_array)):
        return False, "Az időoszlop nem numerikus értékeket tartalmaz.", None
        
    # Check for non-monotonic time (decreasing or duplicate)
    dt_array = np.diff(time_array)
    if np.any(dt_array <= 0):
        return False, "Hibás időbélyegek (csökkenő vagy duplikált időértékek).", None
        
    # Check for uneven sampling (allow small tolerance)
    median_dt = np.median(dt_array)
    if median_dt <= 0:
        return False, "Értelmezhetetlen időalap.", None
        
    actual_fs = 1.0 / median_dt
    
    # Check for large variation in sampling rate (more than 1%)
    max_dt_diff = np.max(np.abs(dt_array - median_dt))
    if max_dt_diff / median_dt > 0.01:
        return False, "Túlzottan egyenetlen mintavétel.", None
        
    # If expected_fs is provided, check if it matches the actual one within 1%
    if expected_fs is not None:
        if abs(actual_fs - expected_fs) / expected_fs > 0.01:
            return True, f"Az időalapból számított mintavételi frekvencia ({actual_fs:.1f} Hz) eltér a megadottól ({expected_fs} Hz). Az időalapot használjuk.", actual_fs
            
    return True, "OK", actual_fs

def convert_unit(signal, unit):
    """Convert signal to standard m/s^2 if provided in g."""
    if unit.lower() == 'g':
        return signal * 9.80665
    return signal

def calculate_time_features(signal):
    """Calculate time-domain statistics."""
    # Signal is already validated and DC-removed
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    cf = peak / rms if rms > 1e-6 else 0
    kurt = kurtosis(signal, fisher=False) # Pearson definition (normal = 3)
    
    return {"rms": rms, "peak": peak, "crest_factor": cf, "kurtosis": kurt}

def calculate_fft(signal, fs):
    """Calculate one-sided amplitude spectrum with proper scaling."""
    n = len(signal)
    
    # Hanning window and coherent amplitude correction factor
    window = np.hanning(n)
    # The coherent gain of a Hanning window is 0.5 (mean of the window)
    # The amplitude correction factor for peak amplitude retrieval is 1/0.5 = 2.0
    coherent_gain = np.mean(window)
    correction_factor = 1.0 / coherent_gain
    
    signal_w = signal * window
    
    yf = rfft(signal_w)
    xf = rfftfreq(n, 1 / fs)
    
    # Amplitude scaling
    # 2.0/n for one-sided spectrum (except DC and Nyquist), multiplied by window correction
    amplitude = (2.0 / n) * np.abs(yf) * correction_factor
    
    # Fix DC and Nyquist scaling (they don't get the factor of 2)
    amplitude[0] = amplitude[0] / 2.0
    if n % 2 == 0:
        amplitude[-1] = amplitude[-1] / 2.0
        
    return xf, amplitude

def calculate_envelope_spectrum(signal, fs, band=(1000, 5000)):
    """Calculate envelope spectrum for bearing diagnostics."""
    n = len(signal)
    
    nyq = 0.5 * fs
    low = band[0]
    high = band[1]
    
    if low >= nyq or low <= 0:
        return False, f"Érvénytelen szűrősáv: alsó határ ({low} Hz) a Nyquist-frekvencián ({nyq} Hz) kívül esik.", np.array([]), np.array([])
        
    if high >= nyq:
         # Limit to slightly below Nyquist to avoid filter instability
         high = nyq * 0.99
         
    if low >= high:
         return False, f"Érvénytelen szűrősáv: alsó határ ({low} Hz) nagyobb vagy egyenlő, mint a felső ({high} Hz).", np.array([]), np.array([])
         
    b, a = butter(4, [low/nyq, high/nyq], btype='band')
    filtered = filtfilt(b, a, signal)
    
    # Hilbert transform for envelope extraction
    analytic_signal = hilbert(filtered)
    amplitude_envelope = np.abs(analytic_signal)
    
    # Remove DC component from envelope before spectrum
    # Edge effects are usually significant, so we could truncate 5% from edges, but for simplicity we keep it standard
    # or apply a window on the envelope.
    envelope_ac = amplitude_envelope - np.mean(amplitude_envelope)
    
    xf, amplitude = calculate_fft(envelope_ac, fs)
    return True, "OK", xf, amplitude

def extract_harmonics(xf, amplitude, rpm, max_order=10):
    """Extract rotational harmonic amplitudes."""
    if rpm <= 0:
        return {}
        
    fr = rpm / 60.0
    harmonics = {}
    df = xf[1] - xf[0] if len(xf) > 1 else 1.0
    search_bins = int(2.0 / df) + 1 # +/- 2Hz search band
    
    for i in range(1, max_order + 1):
        target_f = i * fr
        idx = np.searchsorted(xf, target_f)
        
        # Ensure we are within array bounds
        if 0 <= idx < len(xf):
            start = max(0, idx - search_bins)
            end = min(len(xf), idx + search_bins + 1)
            
            if start < end:
                harmonics[f"{i}x"] = np.max(amplitude[start:end])
            else:
                harmonics[f"{i}x"] = 0.0
        else:
            harmonics[f"{i}x"] = 0.0
            
    # Also look for 0.5x (sub-harmonic)
    target_f_half = 0.5 * fr
    idx_half = np.searchsorted(xf, target_f_half)
    if 0 <= idx_half < len(xf):
        start = max(0, idx_half - search_bins)
        end = min(len(xf), idx_half + search_bins + 1)
        if start < end:
            harmonics["0.5x"] = np.max(amplitude[start:end])
        else:
            harmonics["0.5x"] = 0.0
    else:
        harmonics["0.5x"] = 0.0
            
    return harmonics
