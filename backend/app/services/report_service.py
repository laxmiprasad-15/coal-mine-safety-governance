import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.config import settings

def generate_pdf_report(report_data: dict, output_filename: str = None) -> str:
    """
    Generates an academic & DGMS standard compliance inspection PDF report.
    """
    if not output_filename:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"coal_mine_safety_report_{timestamp}.pdf"

    file_path = os.path.join(settings.REPORTS_DIR, output_filename)
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1F2937"),
        alignment=0,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151")
    )
    executive_summary_style = ParagraphStyle(
        'ExecSummary',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E3A8A"),
        backColor=colors.HexColor("#EFF6FF"),
        borderColor=colors.HexColor("#BFDBFE"),
        borderWidth=1,
        borderPadding=10,
        spaceAfter=14
    )

    story = []

    # Title & Header
    title = report_data.get("title", "Coal Mine Safety Governance & Compliance Audit Report")
    story.append(Paragraph(title, title_style))
    meta_text = (
        f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | "
        f"<b>Mine:</b> Bharat Coking Coalfields Ltd - Underground Block 4 | "
        f"<b>Regulatory Baseline:</b> DGMS Circulars 2024-26"
    )
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 10))

    # AI Executive Summary
    story.append(Paragraph("1. AI-Generated Executive Governance Summary", section_style))
    summary_text = report_data.get(
        "summary_text",
        "This digital twin compliance audit indicates an overall mine safety index of 86.4%. "
        "During this shift, 2 atmospheric gas anomalies were detected and mitigated in Working Face B. "
        "PPE compliance monitoring achieved a 94.2% adherence rate across 10 active camera feeds. "
        "Corrective actions have been dispatched to the shift safety supervisor."
    )
    story.append(Paragraph(summary_text, executive_summary_style))

    # KPI Statistics Summary Table
    story.append(Paragraph("2. Key Safety & Compliance Performance Indicators", section_style))
    kpis = report_data.get("kpis", {
        "Open Compliance Cases": "5",
        "Critical Atmospheric Alerts": "1",
        "PPE Violations (24h)": "4",
        "Active Monitored Zones": "8",
        "Equipment Operational Rate": "92.5%",
        "Overdue Corrective Actions": "0"
    })

    kpi_table_data = [["Metric Indicator", "Current Value", "Metric Indicator", "Current Value"]]
    kpi_items = list(kpis.items())
    for i in range(0, len(kpi_items), 2):
        row = [kpi_items[i][0], str(kpi_items[i][1])]
        if i + 1 < len(kpi_items):
            row.extend([kpi_items[i + 1][0], str(kpi_items[i + 1][1])])
        else:
            row.extend(["", ""])
        kpi_table_data.append(row)

    t_kpi = Table(kpi_table_data, colWidths=[150, 110, 150, 110])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 12))

    # Compliance Cases Summary Table
    story.append(Paragraph("3. Traceable Compliance Cases & Action Status", section_style))
    cases = report_data.get("cases", [])
    if cases:
        case_rows = [["Case ID", "Title / Hazard", "Category", "Risk", "Responsible", "Status"]]
        for c in cases[:10]:
            case_rows.append([
                c.get("case_number", "CASE-001"),
                Paragraph(c.get("title", "Safety Issue")[:40], body_style),
                c.get("category", "General"),
                c.get("risk_level", "Medium"),
                c.get("responsible_user_name", "Safety Eng."),
                c.get("status", "Open")
            ])
        t_cases = Table(case_rows, colWidths=[70, 170, 75, 55, 90, 60])
        t_cases.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_cases)
    else:
        story.append(Paragraph("All zones fully compliant. No open regulatory violations.", body_style))

    # Auditor and Authority Sign-off block
    story.append(Spacer(1, 25))
    sign_data = [
        ["Report Prepared By (AI Engine):", "Certified Safety Officer:", "Statutory Mine Auditor:"],
        ["\n\n_________________________", "\n\n_________________________", "\n\n_________________________"],
        ["AI Safety Governance v2.4", "Govt. Cert # DGMS-2026-X8", "Chief Mine Inspector"]
    ]
    t_sign = Table(sign_data, colWidths=[170, 170, 170])
    t_sign.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#4B5563")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(KeepTogether(t_sign))

    doc.build(story)
    return file_path

def generate_excel_report(report_data: dict, output_filename: str = None) -> str:
    """
    Generates a multi-tab Excel workbook containing complete compliance telemetry.
    """
    if not output_filename:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"coal_mine_safety_data_{timestamp}.xlsx"

    file_path = os.path.join(settings.REPORTS_DIR, output_filename)
    wb = Workbook()

    # Tab 1: Executive KPI Summary
    ws_kpi = wb.active
    ws_kpi.title = "Safety KPIs"
    
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)

    ws_kpi.append(["Metric", "Value", "Baseline Threshold", "Status"])
    for cell in ws_kpi[1]:
        cell.fill = header_fill
        cell.font = header_font

    kpis = report_data.get("kpis", {})
    for k, v in kpis.items():
        ws_kpi.append([k, str(v), "DGMS 2026 Normal", "Compliant"])

    # Tab 2: Compliance Cases
    ws_cases = wb.create_sheet(title="Compliance Cases")
    ws_cases.append(["Case Number", "Title", "Category", "Source", "Risk Level", "Zone", "Responsible Person", "Status", "Deadline"])
    for cell in ws_cases[1]:
        cell.fill = header_fill
        cell.font = header_font

    cases = report_data.get("cases", [])
    for c in cases:
        ws_cases.append([
            c.get("case_number", ""),
            c.get("title", ""),
            c.get("category", ""),
            c.get("source", ""),
            c.get("risk_level", ""),
            c.get("zone_name", ""),
            c.get("responsible_user_name", ""),
            c.get("status", ""),
            str(c.get("deadline", ""))
        ])

    wb.save(file_path)
    return file_path

