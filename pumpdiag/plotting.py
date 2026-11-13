import plotly.graph_objects as go
import numpy as np

def plot_time_series(df, col):
    step = max(1, len(df) // 10000)
    df_plot = df.iloc[::step]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['time_s'], y=df_plot[col], mode='lines', name='Rezgés'))
    fig.update_layout(title=f"Rezgés-időjel ({col})", xaxis_title="Idő [s]", yaxis_title="Gyorsulás [m/s²]")
    return fig

def plot_spectrum(xf, yf, rpm):
    fig = go.Figure()
    mask = xf < 1000
    fig.add_trace(go.Scatter(x=xf[mask], y=yf[mask], mode='lines', name='Spektrum'))
    fr = rpm / 60.0
    for i in range(1, 6):
        fig.add_vline(x=i*fr, line_dash="dash", line_color="red", opacity=0.5)
        fig.add_annotation(x=i*fr, y=max(yf[mask]) * 0.9 if len(yf[mask])>0 else 1, text=f"{i}x", showarrow=False)
    fig.update_layout(title="Amplitúdóspektrum", xaxis_title="Frekvencia [Hz]", yaxis_title="Amplitúdó [m/s²]")
    return fig

def plot_trend(df, col, title, ylabel):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[col], mode='lines+markers'))
    fig.update_layout(title=title, xaxis_title="Idő [s]", yaxis_title=ylabel)
    return fig
