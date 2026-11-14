import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import time
import zipfile

# Add local directory to path to ensure modules are found in Streamlit Cloud
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pumpdiag import demo, signal_processing, diagnostics, plotting, reporting

# Session state initialization
if 'project_state' not in st.session_state:
    st.session_state.project_state = {
        'metadata': {'data_origin': 'ismeretlen'},
        'df_vib': None,
        'df_op': None,
        'config': {
            'fs_expected': 25600,
            'rpm': 1500,
            'channel': None,
            'unit': 'm/s²',
            'env_band': [1000, 5000]
        },
        'results': None,
        'is_stale': False
    }

def update_stale_state():
    """Mark results as stale if inputs change."""
    if st.session_state.project_state['results'] is not None:
        st.session_state.project_state['is_stale'] = True

st.set_page_config(page_title="PumpDiag Web v2.1", layout="wide")

st.title("PumpDiag Web - Szivattyúdiagnosztika v2.1")
st.markdown("*Javított, független vizsgálat alapján validált mérnöki prototípus.*")

# Create tabs
tabs = st.tabs(["Kezdőlap / Bemenet", "Elemzés és Feldolgozás", "Diagramok", "Diagnosztika & Jelentés", "Mentés & Visszatöltés"])

# 1. Bemenet Tab
with tabs[0]:
    st.header("Adatforrás")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Demó adatok betöltése")
        demo_type = st.selectbox("Válassz szimulált hibajelleget:", 
                                 ["Normál állapot", "Tengelybeállítási hiba", "Mechanikai lazaság", "Csapágyhiba"])
        
        fault_map = {
            "Normál állapot": "normal",
            "Tengelybeállítási hiba": "misalignment",
            "Mechanikai lazaság": "looseness",
            "Csapágyhiba": "bearings"
        }
        
        if st.button("Demó betöltése"):
            df_vib, df_op, meta = demo.generate_demo_data(fault_type=fault_map[demo_type])
            st.session_state.project_state['df_vib'] = df_vib
            st.session_state.project_state['df_op'] = df_op
            st.session_state.project_state['metadata'] = meta
            st.session_state.project_state['config']['rpm'] = meta['nominal_rpm']
            st.session_state.project_state['results'] = None
            st.session_state.project_state['is_stale'] = False
            st.success(f"{demo_type} demó sikeresen betöltve!")

    with col2:
        st.subheader("Saját CSV feltöltése")
        uploaded_file = st.file_uploader("Rezgésadat CSV (Várt oszlop: time_s)", type="csv")
        
        if uploaded_file is not None:
            if st.button("CSV Betöltése"):
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'time_s' not in df.columns:
                        st.error("A CSV-nek tartalmaznia kell egy 'time_s' nevű időoszlopot!")
                    else:
                        st.session_state.project_state['df_vib'] = df
                        st.session_state.project_state['metadata'] = {
                            "project_id": "SAJÁT",
                            "machine_id": "Ismeretlen gép",
                            "data_origin": "valós"
                        }
                        st.session_state.project_state['results'] = None
                        st.session_state.project_state['is_stale'] = False
                        st.success("Saját adat sikeresen betöltve!")
                except Exception as e:
                    st.error(f"Hiba a fájl beolvasásakor: {str(e)}")

    if st.session_state.project_state['df_vib'] is not None:
        st.subheader("Bemeneti adat előnézet")
        df_show = st.session_state.project_state['df_vib']
        st.dataframe(df_show.head())
        st.info(f"Betöltve: {len(df_show)} minta, {len(df_show.columns)-1} adatcsatorna.")

# 2. Elemzés Tab
with tabs[1]:
    st.header("Jelfeldolgozási paraméterek")
    
    if st.session_state.project_state['df_vib'] is not None:
        if st.session_state.project_state['is_stale']:
            st.warning("A bemeneti paraméterek megváltoztak! Az eredmények elavultak, új elemzés szükséges.")
            
        df_vib = st.session_state.project_state['df_vib']
        channels = [c for c in df_vib.columns if c != 'time_s']
        
        col1, col2 = st.columns(2)
        with col1:
            cfg_channel = st.selectbox("Elemzendő csatorna", channels, 
                                     index=channels.index(st.session_state.project_state['config'].get('channel')) if st.session_state.project_state['config'].get('channel') in channels else 0,
                                     on_change=update_stale_state)
            
            cfg_unit = st.selectbox("Mértékegység", ["m/s²", "g"], 
                                  index=0 if st.session_state.project_state['config'].get('unit') == "m/s²" else 1,
                                  on_change=update_stale_state)
            
            cfg_rpm = st.number_input("Fordulatszám (RPM)", min_value=1, value=int(st.session_state.project_state['config'].get('rpm', 1500)),
                                    on_change=update_stale_state)
                                    
        with col2:
            st.write("Burkológörbe szűrősáv (Hz):")
            cfg_env_low = st.number_input("Alsó határ", min_value=10, value=st.session_state.project_state['config'].get('env_band', [1000, 5000])[0], on_change=update_stale_state)
            cfg_env_high = st.number_input("Felső határ", min_value=100, value=st.session_state.project_state['config'].get('env_band', [1000, 5000])[1], on_change=update_stale_state)
            
            locs = ["(Ismeretlen)", "csapágyház", "gépláb", "alaplemez"]
            curr_loc = st.session_state.project_state['metadata'].get('measurement_location', "(Ismeretlen)")
            cfg_loc = st.selectbox("Mérési pont lokalizációja", locs, 
                                 index=locs.index(curr_loc) if curr_loc in locs else 0,
                                 on_change=update_stale_state)
        
        if st.button("Elemzés indítása", type="primary"):
            st.session_state.project_state['config'].update({
                'channel': cfg_channel,
                'unit': cfg_unit,
                'rpm': cfg_rpm,
                'env_band': [cfg_env_low, cfg_env_high]
            })
            if cfg_loc != "(Ismeretlen)":
                st.session_state.project_state['metadata']['measurement_location'] = cfg_loc
                
            with st.spinner("Adatminőség ellenőrzése és jelfeldolgozás..."):
                try:
                    t_arr = df_vib['time_s'].values
                    raw_sig = df_vib[cfg_channel].values
                    
                    # Convert unit manually here to avoid attribute error if module reload failed
                    if cfg_unit.lower() == 'g':
                        sig_conv = raw_sig * 9.80665
                    else:
                        sig_conv = raw_sig
                    
                    # Validations
                    time_ok, time_msg, actual_fs = signal_processing.check_time_axis(t_arr)
                    sig_ok, sig_msg, sig_ac = signal_processing.validate_signal(sig_conv, actual_fs)
                    
                    if not time_ok:
                        st.error(f"Kritikus időalap hiba: {time_msg}")
                        st.session_state.project_state['results'] = None
                    elif not sig_ok:
                        st.error(f"Kritikus adatminőségi hiba: {sig_msg}")
                        st.session_state.project_state['results'] = None
                    else:
                        if time_msg != "OK":
                            st.warning(time_msg)
                            
                        # Process
                        features = signal_processing.calculate_time_features(sig_ac)
                        xf, yf = signal_processing.calculate_fft(sig_ac, actual_fs)
                        
                        env_ok, env_msg, exf, eyf = signal_processing.calculate_envelope_spectrum(sig_ac, actual_fs, band=(cfg_env_low, cfg_env_high))
                        if not env_ok:
                            st.warning(f"Burkológörbe számítás sikertelen: {env_msg}")
                            env_features = None
                        else:
                            env_features = {'has_peaks': np.max(eyf) > 0.05} if len(eyf) > 0 else None
                        
                        harmonics = signal_processing.extract_harmonics(xf, yf, cfg_rpm)
                        
                        primary, diag_res = diagnostics.evaluate_diagnostics(
                            features, harmonics, cfg_rpm, env_features, st.session_state.project_state['metadata']
                        )
                        
                        st.session_state.project_state['results'] = {
                            "channel": cfg_channel,
                            "features": features,
                            "xf": xf, "yf": yf,
                            "exf": exf, "eyf": eyf,
                            "primary_result": primary,
                            "diag_results": diag_res
                        }
                        st.session_state.project_state['is_stale'] = False
                        st.success("Elemzés és diagnosztika sikeresen befejeződött!")
                except Exception as e:
                    st.error(f"Váratlan hiba történt az elemzés során: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    else:
        st.info("Kérjük, előbb töltsön be adatot az első fülön.")

# 3. Diagramok Tab
with tabs[2]:
    st.header("Interaktív diagramok")
    
    if st.session_state.project_state['results'] is not None and not st.session_state.project_state['is_stale']:
        res = st.session_state.project_state['results']
        df = st.session_state.project_state['df_vib']
        
        st.plotly_chart(plotting.plot_time_series(df, res['channel']), use_container_width=True)
        st.plotly_chart(plotting.plot_spectrum(res['xf'], res['yf'], st.session_state.project_state['config']['rpm']), use_container_width=True)
        
        if len(res['exf']) > 0:
            st.plotly_chart(plotting.plot_spectrum(res['exf'], res['eyf'], st.session_state.project_state['config']['rpm'], is_envelope=True), use_container_width=True)
            
        df_op = st.session_state.project_state.get('df_op')
        if df_op is not None and 'speed_rpm' in df_op.columns:
            st.plotly_chart(plotting.plot_trend(df_op, 'speed_rpm', 'Fordulatszám trend', 'RPM'), use_container_width=True)
            
    elif st.session_state.project_state['is_stale']:
        st.warning("Az adatok megváltoztak, kérjük futtassa újra az elemzést!")
    else:
        st.info("Futtassa le az elemzést a diagramok megtekintéséhez.")

# 4. Diagnosztika Tab
with tabs[3]:
    st.header("Diagnosztikai Eredmények")
    
    if st.session_state.project_state['results'] is not None and not st.session_state.project_state['is_stale']:
        res = st.session_state.project_state['results']
        
        st.info(f"**Elsődleges megállapítás:** {res['primary_result']}")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Időtartományi Mutatók")
            f = res['features']
            st.metric("RMS", f"{f['rms']:.4f} m/s²")
            st.metric("Csúcs (Peak)", f"{f['peak']:.4f} m/s²")
            st.metric("Kurtózis", f"{f['kurtosis']:.4f}")
            st.metric("Csúcstényező", f"{f['crest_factor']:.4f}")
            
        with col2:
            st.subheader("Részletes Bizonyítékok")
            for d in res['diag_results']:
                exp_title = f"{d['name']} - {d['status'].upper()}"
                if d['status'] == "támogatott":
                    exp_title += f" ({d['support_level']})"
                    
                with st.expander(exp_title):
                    if d['support']:
                        st.write("**Támogató bizonyítékok:**")
                        for s in d['support']: st.write(f"✅ {s}")
                    
                    if d['contradict']:
                        st.write("**Ellentmondó bizonyítékok:**")
                        for c in d['contradict']: st.write(f"❌ {c}")
                        
                    if d['missing']:
                        st.write("**Hiányzó információk:**")
                        for m in d['missing']: st.write(f"⚠️ {m}")
                        
                    st.write(f"**Javaslat:** *{d['recommendation']}*")
                    
        st.subheader("Jelentés Letöltése")
        pdf_buf = reporting.create_pdf_report(st.session_state.project_state)
        st.download_button(
            label="📄 PDF Jelentés letöltése",
            data=pdf_buf.getvalue(),
            file_name="PumpDiag_Jelentes.pdf",
            mime="application/pdf"
        )
        
    elif st.session_state.project_state['is_stale']:
        st.warning("Elavult eredmények. Kérjük futtassa újra az elemzést!")
    else:
        st.info("Nincs értékelhető eredmény.")

# 5. Mentés Tab
with tabs[4]:
    st.header("Projekt Mentése és Visszatöltése")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Projekt letöltése")
        st.write("Menti a teljes munkamenetet (adatok, beállítások, eredmények).")
        if st.session_state.project_state['df_vib'] is not None:
            zip_data = reporting.create_project_zip(st.session_state.project_state)
            st.download_button(
                label="📦 Projekt ZIP letöltése",
                data=zip_data,
                file_name="pumpdiag_project.zip",
                mime="application/zip"
            )
        else:
            st.info("Nincs menthető adat.")
            
    with col2:
        st.subheader("Projekt visszatöltése")
        proj_file = st.file_uploader("Korábban mentett ZIP feltöltése", type="zip")
        if proj_file is not None and st.button("Projekt helyreállítása"):
            try:
                with zipfile.ZipFile(proj_file, 'r') as z:
                    files = z.namelist()
                    if "metadata.json" in files and "vibration_data.csv" in files:
                        meta = json.loads(z.read("metadata.json").decode('utf-8'))
                        cfg = json.loads(z.read("config.json").decode('utf-8')) if "config.json" in files else {}
                        
                        csv_data = io.BytesIO(z.read("vibration_data.csv"))
                        df = pd.read_csv(csv_data)
                        
                        st.session_state.project_state['metadata'] = meta
                        st.session_state.project_state['config'].update(cfg)
                        st.session_state.project_state['df_vib'] = df
                        
                        st.session_state.project_state['results'] = None
                        st.session_state.project_state['is_stale'] = True
                        
                        st.success("Projekt sikeresen betöltve! Kérjük, futtassa újra az elemzést a paraméterek érvényesítéséhez.")
                    else:
                        st.error("Érvénytelen projektfájl: Hiányzó metadata.json vagy vibration_data.csv")
            except Exception as e:
                st.error(f"Hiba a projekt betöltésekor: {str(e)}")
