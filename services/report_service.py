"""
services/report_service.py — PDF and text report generation
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ReportService:
    """Service for generating PDF health reports."""

    BRAND_COLOR = colors.HexColor("#1a56db")
    ACCENT_COLOR = colors.HexColor("#7c3aed")
    WARNING_COLOR = colors.HexColor("#d97706")
    DANGER_COLOR = colors.HexColor("#dc2626")
    SUCCESS_COLOR = colors.HexColor("#059669")
    BG_LIGHT = colors.HexColor("#f8fafc")

    @staticmethod
    def generate_pdf(patient: dict, report_content: str,
                     stats: dict, report_type: str) -> bytes:
        """
        Generate a professional PDF health report.

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        story = []

        # ------ Custom styles ------
        title_style = ParagraphStyle(
            "ChronicCareTitle",
            parent=styles["Title"],
            fontSize=22,
            textColor=ReportService.BRAND_COLOR,
            spaceAfter=4,
            alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#6b7280"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=ReportService.BRAND_COLOR,
            spaceBefore=12,
            spaceAfter=4,
            borderPad=(0, 0, 2, 0),
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )
        label_style = ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#6b7280"),
        )

        # ------ Header ------
        story.append(Paragraph("ChronicCare AI", title_style))
        story.append(Paragraph(
            f"Intelligent Chronic Disease Monitoring Report — {report_type.capitalize()}",
            subtitle_style,
        ))
        story.append(Paragraph(
            f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} | Powered by IBM Granite",
            label_style,
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=ReportService.BRAND_COLOR))
        story.append(Spacer(1, 12))

        # ------ Patient Info Table ------
        story.append(Paragraph("Patient Information", heading_style))
        patient_data = [
            ["Name", patient.get("name", "N/A"), "Disease", patient.get("primary_disease", "N/A")],
            ["Age / Gender", f"{patient.get('age', 'N/A')} / {patient.get('gender', 'N/A')}",
             "Blood Group", patient.get("blood_group", "N/A")],
            ["Doctor", patient.get("doctor_name", "N/A"),
             "Next Appointment", patient.get("next_appointment", "N/A")],
            ["BMI", str(patient.get("bmi", "N/A")),
             "Allergies", patient.get("known_allergies", "None")],
        ]
        t = Table(patient_data, colWidths=[1.2 * inch, 2.3 * inch, 1.2 * inch, 2.3 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), ReportService.BG_LIGHT),
            ("BACKGROUND", (2, 0), (2, -1), ReportService.BG_LIGHT),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, ReportService.BG_LIGHT]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

        # ------ Health Stats Summary ------
        if stats:
            story.append(Paragraph(f"Health Statistics ({stats.get('count', 0)} Records)", heading_style))
            stats_data = [
                ["Metric", "Average Value", "Target Range", "Status"],
                ["Blood Glucose", f"{stats.get('avg_glucose', 'N/A')} mg/dL", "70–180 mg/dL",
                 "⚠️ Monitor" if (stats.get("avg_glucose") or 0) > 180 else "✓ OK"],
                ["Blood Pressure", f"{stats.get('avg_systolic', 'N/A')}/{stats.get('avg_diastolic', 'N/A')} mmHg",
                 "< 140/90 mmHg",
                 "⚠️ High" if (stats.get("avg_systolic") or 0) > 140 else "✓ OK"],
                ["Heart Rate", f"{stats.get('avg_hr', 'N/A')} bpm", "60–100 bpm", "✓ OK"],
                ["Oxygen Saturation", f"{stats.get('avg_o2', 'N/A')}%", "≥ 95%",
                 "⚠️ Low" if (stats.get("avg_o2") or 100) < 94 else "✓ OK"],
                ["Health Score", f"{stats.get('avg_health_score', 'N/A')}/100", "≥ 75", ""],
                ["Avg Sleep", f"{stats.get('avg_sleep', 'N/A')} hrs", "7–9 hrs", ""],
                ["Avg Exercise", f"{stats.get('avg_exercise', 'N/A')} min/day", "≥ 30 min", ""],
            ]
            st = Table(stats_data, colWidths=[1.8 * inch, 1.7 * inch, 1.7 * inch, 1.8 * inch])
            st.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), ReportService.BRAND_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ReportService.BG_LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(st)
            story.append(Spacer(1, 10))

        # ------ AI Report Content ------
        story.append(Paragraph("AI-Generated Health Analysis", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
        story.append(Spacer(1, 6))

        # Split report content into paragraphs
        for line in report_content.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
            elif line.startswith("##") or line.startswith("**") and line.endswith("**"):
                clean = line.replace("#", "").replace("**", "").strip()
                story.append(Paragraph(clean, heading_style))
            else:
                clean = line.replace("**", "").replace("*", "").strip("•-")
                if clean:
                    story.append(Paragraph(clean, body_style))

        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))

        # ------ Disclaimer ------
        disclaimer = (
            "<i>DISCLAIMER: This report is generated by ChronicCare AI powered by IBM Granite models. "
            "It is intended as a supplementary health monitoring tool and does NOT replace professional "
            "medical advice, diagnosis, or treatment. Always consult your healthcare provider for "
            "medical decisions.</i>"
        )
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            disclaimer,
            ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8,
                           textColor=colors.HexColor("#9ca3af"), leading=12),
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
