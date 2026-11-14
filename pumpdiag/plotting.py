import plotly.graph_objects as go
import numpy as np

def plot_time_series(df, col):
    """Interactive time series plot with peak-preserving decimation."""
    # Peak-preserving decimation to handle large files in browser
    # We want to keep approx 5000 points for smooth UI, but preserve peaks
    n_points = len(df)
    target_points = 5000
    
    if n_points <= target_points:
        df_plot = df
        t = df['time_s'].values
        y = df[col].values
    else:
        step = n_points // target_points
        # Reshape to chunks and take min/max of each chunk
        chunks = n_points // step
        y_vals = df[col].values[:chunks*step].reshape(chunks, step)
        t_vals = df['time_s'].values[:chunks*step].reshape(chunks, step)
        
        y_max = np.max(y_vals, axis=1)
        y_min = np.min(y_vals, axis=1)
        t_mean = np.mean(t_vals, axis=1)
        
        # Interleave min and max to preserve envelope
        y = np.empty(chunks * 2)
        y[0::2] = y_min
        y[1::2] = y_max
        t = np.empty(chunks * 2)
        t[0::2] = t_mean
        t[1::2] = t_mean
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=y, mode='lines', name='Rezgés'))
    
    # Generate unique ID for the plot based on column name to avoid DuplicateElementId
    fig_id = f"ts_{col}"
    
    fig.update_layout(
        title=f"Rezgés-időjel ({col})", 
        xaxis_title="Idő [s]", 
        yaxis_title="Gyorsulás [m/s²]",
        uirevision=fig_id # Helps keep zoom state if data updates
    )
    return fig

def plot_spectrum(xf, yf, rpm, is_envelope=False):
    """Amplitude spectrum with rotational harmonic markers."""
    fig = go.Figure()
    
    # Filter spectrum for display (usually most info is < 1000Hz for base diagnostics)
    mask = xf <= min(1000, np.max(xf)) if len(xf) > 0 else np.array([True])
    
    if len(xf[mask]) > 0:
        name = 'Burkológörbe-spektrum' if is_envelope else 'Amplitúdóspektrum'
        fig.add_trace(go.Scatter(x=xf[mask], y=yf[mask], mode='lines', name=name))
        
        if rpm > 0:
            fr = rpm / 60.0
            max_y = np.max(yf[mask]) if len(yf[mask]) > 0 else 1.0
            
            # Add harmonic markers
            for i in range(1, 11): # Up to 10x
                hx = i * fr
                if hx <= np.max(xf[mask]):
                    fig.add_vline(x=hx, line_dash="dash", line_color="rgba(255,0,0,0.3)")
                    # Only annotate first 5 to avoid clutter
                    if i <= 5:
                        fig.add_annotation(x=hx, y=max_y * 0.9, text=f"{i}x", showarrow=False, font=dict(color="red", size=10))
            
            # Sub-harmonic
            if 0.5 * fr <= np.max(xf[mask]):
                fig.add_vline(x=0.5*fr, line_dash="dot", line_color="rgba(255,165,0,0.5)")
                fig.add_annotation(x=0.5*fr, y=max_y * 0.8, text="0.5x", showarrow=False, font=dict(color="orange", size=10))
                
    title = "Burkológörbe-spektrum (Demodulált)" if is_envelope else "Amplitúdóspektrum"
    
    fig.update_layout(
        title=title, 
        xaxis_title="Frekvencia [Hz]", 
        yaxis_title="Amplitúdó [m/s²]",
        yaxis=dict(rangemode='tozero')
    )
    return fig

def plot_trend(df, col, title, ylabel):
    """Trend plot for operational data."""
    fig = go.Figure()
    if col in df.columns:
        fig.add_trace(go.Scatter(x=df['timestamp' if 'timestamp' in df.columns else df.columns[0]], 
                                 y=df[col], mode='lines+markers', name=title))
    fig.update_layout(title=title, xaxis_title="Idő", yaxis_title=ylabel)
    return fig
