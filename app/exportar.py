# exportar.py
# Funciones para exportar a Excel y PDF

from pathlib import Path
import pandas as pd
import datetime
from diseño_premium import COLORS

# ReportLab (PDF)
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Carpeta de exportaciones
OUTPUT_DIR = Path(__file__).parent / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def exportar_excel(data: list) -> str:
    """
    Exporta asistencias a Excel usando pandas.
    data: lista de dicts con las nuevas columnas.
    """
    columnas = ["Nombre", "Cédula", "Fecha", "Turno", "Llegada", "Salida", "Horas", "Tarde"]

    df = pd.DataFrame(data if data else [], columns=columnas)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"asistencias_{ts}.xlsx"

    df.to_excel(path, index=False, engine='openpyxl')

    return str(path)


def exportar_pdf(data: list) -> str:
    """
    Exporta asistencias a PDF (formato horizontal).
    data: lista de filas [Nombre, Cédula, Fecha, Turno, Llegada, Salida, Horas, Tarde]
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"asistencias_{ts}.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    flow = []

    # Título con color azul moderno
    titulo = Paragraph("<b>Reporte de Asistencia | Control de Personal</b>", styles["Title"])
    flow.append(titulo)
    flow.append(Spacer(1, 12))
    
    # Fecha de generación
    fecha_gen = Paragraph(
        f"<i>Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
        styles["Normal"]
    )
    flow.append(fecha_gen)
    flow.append(Spacer(1, 20))

    # Encabezados
    tabla_data = [["Nombre", "Cédula", "Fecha", "Turno", "Llegada", "Salida", "Horas Trabajadas", "Tarde"]]

    # Datos
    if data:
        tabla_data.extend(data)

    # Construir tabla
    tabla = Table(tabla_data, repeatRows=1)

    tabla.setStyle(TableStyle([
        # Encabezado con color azul moderno
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Cuerpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#2563EB")),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    flow.append(tabla)
    
    # Pie de página
    flow.append(Spacer(1, 20))
    pie = Paragraph(
        "<i>Sistema de Control de Personal - Todos los derechos reservados</i>",
        styles["Normal"]
    )
    flow.append(pie)
    
    doc.build(flow)

    return str(path)