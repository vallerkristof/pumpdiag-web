import io
import json
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
# Enable unicode support
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Create a dummy font if no TTF is available to ensure it doesn't crash
# In a real app, we'd bundle a TTF font. Since we can't easily download one here reliably, 
# we'll define a mapping to handle Hungarian characters with standard fonts as a fallback,
# but try to register a standard Windows font if it exists.
def setup_fonts():
    try:
        # Try to use standard fonts that support CE (Central European)
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        return 'FreeSans'
    except:
        try:
            # Try Windows default
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            return 'Arial'
        except:
            return 'Helvetica'

def create_pdf_report(project_state):
    """Generate a comprehensive PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=18)
    
    font_name = setup_fonts()
    
    # Custom styles to support unicode if font is available
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontName=font_name)
    h2_style = ParagraphStyle('CustomH2', parent=styles['Heading2'], fontName=font_name)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontName=font_name)
    
    # Replace unicode characters if using Helvetica fallback
    def clean_text(text):
        if font_name == 'Helvetica' and isinstance(text, str):
            replacements = {'ő': 'o', 'ű': 'u', 'Ő': 'O', 'Ű': 'U'}
            for k, v in replacements.items():
                text = text.replace(k, v)
        return text

    Story = []
    
    meta = project_state.get('metadata', {})
    res = project_state.get('results', {})
    
    if not res:
        Story.append(Paragraph(clean_text("Nincs elérhető eredmény a jelentéshez."), normal_style))
        doc.build(Story)
        buffer.seek(0)
        return buffer
        
    Story.append(Paragraph(clean_text("PumpDiag Web - Diagnosztikai Jelentés"), title_style))
    Story.append(Spacer(1, 20))
    
    # 1. Gép- és mérésazonosítás
    Story.append(Paragraph(clean_text("1. Gép- és mérésazonosítás"), h2_style))
    Story.append(Paragraph(clean_text(f"Gépazonosító: {meta.get('machine_id', 'N/A')}"), normal_style))
    Story.append(Paragraph(clean_text(f"Adat eredete: {meta.get('data_origin', 'ismeretlen')}"), normal_style))
    Story.append(Paragraph(clean_text(f"Névleges fordulatszám: {meta.get('nominal_rpm', 'N/A')} RPM"), normal_style))
    Story.append(Paragraph(clean_text(f"Elemzett csatorna: {res.get('channel', 'N/A')}"), normal_style))
    Story.append(Spacer(1, 15))
    
    # 2. Elsődleges megállapítás
    Story.append(Paragraph(clean_text("2. Diagnosztikai megállapítások"), h2_style))
    Story.append(Paragraph(clean_text(f"<b>Elsődleges megállapítás:</b> {res.get('primary_result', 'N/A')}"), normal_style))
    Story.append(Spacer(1, 15))
    
    # 3. Számított mutatók
    Story.append(Paragraph(clean_text("3. Számított jellemzők"), h2_style))
    features = res.get('features', {})
    
    data = [["Mutató", "Érték"]]
    if 'rms' in features: data.append(["RMS [m/s²]", f"{features['rms']:.4f}"])
    if 'peak' in features: data.append(["Csúcs (Peak) [m/s²]", f"{features['peak']:.4f}"])
    if 'crest_factor' in features: data.append(["Csúcstényező (Crest factor)", f"{features['crest_factor']:.4f}"])
    if 'kurtosis' in features: data.append(["Kurtózis", f"{features['kurtosis']:.4f}"])
    
    # Clean table data if needed
    clean_data = [[clean_text(str(cell)) for cell in row] for row in data]
    
    t = Table(clean_data, style=[
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,-1), font_name)
    ])
    Story.append(t)
    Story.append(Spacer(1, 15))
    
    # 4. Bizonyítékok
    Story.append(Paragraph(clean_text("4. Diagnosztikai bizonyítékok és jelöltek"), h2_style))
    diagnostics = res.get('diag_results', [])
    
    for diag in diagnostics:
        Story.append(Paragraph(clean_text(f"<b>{diag['name']}</b>"), normal_style))
        Story.append(Paragraph(clean_text(f"Állapot: {diag['status']} (Alátámasztottság: {diag.get('support_level', '-')})"), normal_style))
        
        if diag['support']:
            Story.append(Paragraph(clean_text("Támogató bizonyítékok:"), normal_style))
            for s in diag['support']:
                Story.append(Paragraph(clean_text(f"• {s}"), normal_style))
                
        if diag['contradict']:
            Story.append(Paragraph(clean_text("Ellentmondó bizonyítékok:"), normal_style))
            for c in diag['contradict']:
                Story.append(Paragraph(clean_text(f"• {c}"), normal_style))
                
        if diag.get('missing'):
            Story.append(Paragraph(clean_text("Hiányzó adatok:"), normal_style))
            for m in diag['missing']:
                Story.append(Paragraph(clean_text(f"• {m}"), normal_style))
                
        Story.append(Paragraph(clean_text(f"<i>Javaslat: {diag.get('recommendation', '')}</i>"), normal_style))
        Story.append(Spacer(1, 10))
        
    Story.append(Spacer(1, 20))
    Story.append(Paragraph(clean_text("Készült a PumpDiag Web mérnöki prototípus segítségével. A jelentés nem minősül hivatalos szakvéleménynek."), normal_style))
    
    doc.build(Story)
    buffer.seek(0)
    return buffer

def create_project_zip(project_state):
    """Create a ZIP file containing all project data for round-trip."""
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # Save metadata
        z.writestr("metadata.json", json.dumps(project_state.get('metadata', {}), indent=2))
        
        # Save results if available
        if project_state.get('results'):
            # We don't save raw arrays (xf, yf) in JSON due to size, we just save features and diagnostics
            res_summary = {k: v for k, v in project_state['results'].items() if k not in ['xf', 'yf', 'exf', 'eyf']}
            z.writestr("results.json", json.dumps(res_summary, indent=2))
            
        # Save configuration used
        z.writestr("config.json", json.dumps(project_state.get('config', {}), indent=2))
        
        # Save raw data if available (convert dataframe to CSV)
        if 'df_vib' in project_state and project_state['df_vib'] is not None:
            csv_str = project_state['df_vib'].to_csv(index=False)
            z.writestr("vibration_data.csv", csv_str)
            
    return zip_buf.getvalue()
