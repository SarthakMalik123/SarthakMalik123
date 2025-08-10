from __future__ import annotations
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from typing import Dict
import pandas as pd


def export_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_pdf_summary(kpis: Dict[str, float]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, "SurakshitPath – Summary Report")

    c.setFont("Helvetica", 11)
    y = height - 3*cm
    for label, value in kpis.items():
        c.drawString(2*cm, y, f"{label}: {value}")
        y -= 0.8*cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()