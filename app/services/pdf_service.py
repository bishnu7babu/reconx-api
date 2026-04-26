from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, LongTable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime


def get_risk_color(risk_level: str):
    colors_map = {
        "Critical": colors.HexColor("#DC2626"),
        "High": colors.HexColor("#EA580C"),
        "Medium": colors.HexColor("#D97706"),
        "Low": colors.HexColor("#059669"),
        "Info": colors.HexColor("#2563EB"),
    }
    return colors_map.get(risk_level, colors.HexColor("#6B7280"))


def generate_pdf_report(
        scan_id: str,
        host: str,
        started_at: str,
        nmap_output: str,
        harvester_output: str,
        subfinder_output: str,
        ai_summary: dict
) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    elements = []

    # =============================
    # STYLES
    # =============================

    title_style = ParagraphStyle(
        "Title",
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=26
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#D1D5DB"),
        alignment=TA_CENTER,
        leading=14
    )

    section_style = ParagraphStyle(
        "Section",
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"),
        spaceAfter=8,
        spaceBefore=16,
        leading=16
    )

    normal_style = ParagraphStyle(
        "Normal",
        fontSize=10,
        fontName="Helvetica",
        leading=14,
        spaceAfter=6,
        textColor=colors.HexColor("#374151")
    )

    raw_line_style = ParagraphStyle(
        "RawLine",
        fontSize=8,
        fontName="Courier",
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=0,
        spaceBefore=0,
    )

    footer_style = ParagraphStyle(
        "Footer",
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#9CA3AF"),
        spaceBefore=6
    )

    # =============================
    # HEADER BANNER
    # =============================

    header_data = [
        [Paragraph("ReconX Security Report", title_style)],
        [Paragraph("Attack Surface Reconnaissance", subtitle_style)]
    ]
    header_table = Table(header_data, colWidths=[6.8 * inch])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # =============================
    # SCAN INFO
    # =============================

    elements.append(Paragraph("Scan Information", section_style))

    scan_data = [
        ["Target", host],
        ["Scan ID", scan_id],
        ["Date", started_at],
        ["Tools", "nmap, theHarvester, subfinder"],
    ]

    scan_table = Table(scan_data, colWidths=[1.3 * inch, 5.5 * inch])
    scan_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(scan_table)

    # =============================
    # AI SUMMARY
    # =============================

    if ai_summary and "error" not in ai_summary:

        elements.append(Paragraph("AI Attack Surface Analysis", section_style))

        risk_level = ai_summary.get("risk_level", "Unknown")
        risk_score = ai_summary.get("risk_score", 0)
        risk_color = get_risk_color(risk_level)

        # Risk Score Box
        risk_data = [[f"{risk_score}/100 — {risk_level.upper()} RISK"]]
        risk_table = Table(risk_data, colWidths=[6.8 * inch])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), risk_color),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 18),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        elements.append(risk_table)
        elements.append(Spacer(1, 0.1 * inch))

        # Narrative
        narrative = ai_summary.get("threat_narrative", "")
        if narrative:
            elements.append(Paragraph(narrative, normal_style))

        # =============================
        # KEY FINDINGS
        # =============================

        elements.append(Paragraph("Key Findings", section_style))

        findings = ai_summary.get("key_findings", [])

        for finding in findings:
            severity = finding.get("severity", "Info")
            text = finding.get("finding", "")
            sev_color = get_risk_color(severity)

            badge_para = Paragraph(
                f'<b>{severity.upper()}</b>',
                ParagraphStyle(
                    "BadgeText",
                    fontSize=9,
                    fontName="Helvetica-Bold",
                    textColor=colors.white,
                    alignment=TA_CENTER,
                    leading=12
                )
            )

            text_para = Paragraph(text, normal_style)

            finding_table = Table(
                [[badge_para, text_para]],
                colWidths=[0.85 * inch, 5.95 * inch],
                splitByRow=1
            )
            finding_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), sev_color),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FAFAFA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("TOPPADDING", (0, 0), (0, 0), 5),
                ("BOTTOMPADDING", (0, 0), (0, 0), 5),
                ("LEFTPADDING", (0, 0), (0, 0), 4),
                ("RIGHTPADDING", (0, 0), (0, 0), 4),
                ("TOPPADDING", (1, 0), (1, 0), 6),
                ("BOTTOMPADDING", (1, 0), (1, 0), 6),
                ("LEFTPADDING", (1, 0), (1, 0), 10),
                ("RIGHTPADDING", (1, 0), (1, 0), 10),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ]))

            elements.append(KeepTogether(finding_table))
            elements.append(Spacer(1, 0.06 * inch))

    # =============================
    # TOOL OUTPUTS
    # =============================

    tools = [
        ("nmap Results", nmap_output),
        ("theHarvester Results", harvester_output),
        ("subfinder Results", subfinder_output),
    ]

    for name, output in tools:
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")))
        elements.append(Paragraph(name, section_style))

        if output:
            # Escape HTML
            safe = (
                output.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            # Truncate if needed
            if len(safe) > 4000:
                safe = safe[:4000] + "\n... (truncated)"

            # FIX: Split into lines so LongTable can paginate row-by-row
            lines = safe.splitlines()
            table_data = []
            for line in lines:
                # Preserve empty lines with a space so the row has height
                display_line = line if line.strip() else " "
                table_data.append([Paragraph(display_line, raw_line_style)])

            code_table = LongTable(
                table_data,
                colWidths=[6.8 * inch],
                splitByRow=1,
                repeatRows=0,
            )
            code_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F4F6")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ]))
            elements.append(code_table)
        else:
            elements.append(Paragraph("No output available.", normal_style))

    # =============================
    # FOOTER
    # =============================

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")))
    elements.append(
        Paragraph(
            f"Generated by ReconX | {datetime.now().strftime('%Y-%m-%d %H:%M')} | Confidential",
            footer_style
        )
    )

    # =============================
    # BUILD
    # =============================

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()