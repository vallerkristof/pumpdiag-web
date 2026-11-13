import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def create_pdf_report(meta, features, primary_result, diagnostics):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    Story = []
    Story.append(Paragraph("PumpDiag Web - Diagnosztikai Jelentes", styles['Title']))
    Story.append(Spacer(1, 12))
    Story.append(Paragraph(f"Elsodleges megallapitas: {primary_result}", styles['Heading2']))
    Story.append(Spacer(1, 12))
    
    data = [["Mutato", "Ertek"]]
    for k, v in features.items(): data.append([k, f"{v:.3f}"])
    t = Table(data, style=[('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 1, colors.black)])
    Story.append(t)
    Story.append(Spacer(1, 12))
    
    for diag in diagnostics:
        Story.append(Paragraph(f"{diag['name']} - Allapot: {diag['status']}", styles['Normal']))
    
    doc.build(Story)
    buffer.seek(0)
    return buffer
