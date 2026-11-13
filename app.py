import streamlit as st
import pandas as pd
import json
from pumpdiag import demo, signal_processing, diagnostics, plotting, reporting
import zipfile
import io

st.set_page_config(page_title="PumpDiag Web", layout="wide")
if 'data_loaded' not in st.session_state: st.session_state.data_loaded = False
if 'analysis_done' not in st.session_state: st.session_state.analysis_done = False

st.title("PumpDiag Web - Szivattyúdiagnosztika")
tabs = st.tabs(["Kezdőlap / Adat", "Elemzés", "Diagramok", "Diagnosztika & Jelentés", "Mentés"])

with tabs[0]:
    st.header("Adat feltöltése vagy Demó")
    if st.button("Tengelybeállítási hiba demó betöltése"):
        df_vib, df_op, meta = demo.generate_demo_data(fault_type="misalignment")
        st.session_state.df_vib, st.session_state.df_op, st.session_state.meta = df_vib, df_op, meta
        st.session_state.data_loaded = True
        st.success("Demó betöltve.")
    if st.button("Csapágyhiba demó betöltése"):
        df_vib, df_op, meta = demo.generate_demo_data(fault_type="bearings")
        st.session_state.df_vib, st.session_state.df_op, st.session_state.meta = df_vib, df_op, meta
        st.session_state.data_loaded = True
        st.success("Demó betöltve.")
    
    uploaded_file = st.file_uploader("Vagy tölts fel saját CSV-t", type="csv")
    if uploaded_file is not None:
        st.session_state.df_vib = pd.read_csv(uploaded_file)
        st.session_state.meta = {"nominal_rpm": 1480, "data_origin": "valós"}
        st.session_state.data_loaded = True

with tabs[1]:
    if st.session_state.data_loaded:
        channel = st.selectbox("Csatorna", [c for c in st.session_state.df_vib.columns if c != 'time_s'])
        rpm = st.number_input("Fordulatszám", value=st.session_state.meta.get('nominal_rpm', 1480))
        if st.button("Elemzés indítása"):
            signal = st.session_state.df_vib[channel].values
            features = signal_processing.calculate_time_features(signal)
            xf, yf = signal_processing.calculate_fft(signal, 25600)
            exf, eyf = signal_processing.calculate_envelope_spectrum(signal, 25600)
            harmonics = signal_processing.extract_harmonics(xf, yf, rpm)
            primary_result, diag_results = diagnostics.evaluate_diagnostics(features, harmonics, rpm)
            
            st.session_state.res = {
                "channel": channel, "rpm": rpm, "features": features,
                "xf": xf, "yf": yf, "exf": exf, "eyf": eyf,
                "primary_result": primary_result, "diag_results": diag_results
            }
            st.session_state.analysis_done = True
            st.success("Elemzés kész!")

with tabs[2]:
    if st.session_state.analysis_done:
        res = st.session_state.res
        st.plotly_chart(plotting.plot_time_series(st.session_state.df_vib, res['channel']))
        st.plotly_chart(plotting.plot_spectrum(res['xf'], res['yf'], res['rpm']))
        if len(res['exf'])>0: st.plotly_chart(plotting.plot_spectrum(res['exf'], res['eyf'], res['rpm']))

with tabs[3]:
    if st.session_state.analysis_done:
        st.info(st.session_state.res['primary_result'])
        st.json(st.session_state.res['features'])
        pdf_buffer = reporting.create_pdf_report(st.session_state.meta, st.session_state.res['features'], st.session_state.res['primary_result'], st.session_state.res['diag_results'])
        st.download_button("PDF Letöltése", data=pdf_buffer, file_name="jelentes.pdf", mime="application/pdf")

with tabs[4]:
    if st.session_state.analysis_done:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as z:
            z.writestr("meta.json", json.dumps(st.session_state.meta))
            z.writestr("eredmeny.json", json.dumps(st.session_state.res['diag_results']))
        st.download_button("Projekt mentése (ZIP)", data=zip_buf.getvalue(), file_name="projekt.zip", mime="application/zip")
