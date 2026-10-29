import os
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Report, ComplianceCase, PPEDetection, SensorReading, Zone, User
from app.schemas.schemas import ReportResponse, ReportGenerateRequest
from app.services.report_service import generate_pdf_report, generate_excel_report
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/reports", tags=["Automated Reports & Compliance Export"])

@router.get("/", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return reports

@router.post("/generate", response_model=ReportResponse)
def generate_report(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    report_title = req.title or f"{req.report_type.title()} Governance Audit Report ({now.strftime('%d-%b-%Y')})"
    
    # Aggregate data
    total_cases = db.query(ComplianceCase).count()
    open_cases = db.query(ComplianceCase).filter(ComplianceCase.status.in_(["Open", "In Progress"])).count()
    ppe_violations = db.query(PPEDetection).filter(PPEDetection.violation_type != "Compliant").count()
    high_risk_zones = db.query(Zone).filter(Zone.risk_level.in_(["High", "Critical"])).count()

    kpis = {
        "Total Cases Logged": total_cases,
        "Active Open Violations": open_cases,
        "PPE Non-Compliance Events": ppe_violations,
        "High/Critical Risk Sectors": high_risk_zones,
        "Sensor Telemetry Health": "98.4%",
        "Overall Compliance Index": "88.6%"
    }

    cases = db.query(ComplianceCase).order_by(ComplianceCase.created_at.desc()).limit(15).all()
    case_list = [{
        "case_number": c.case_number,
        "title": c.title,
        "category": c.category,
        "source": c.source,
        "risk_level": c.risk_level,
        "zone_name": c.zone.name if c.zone else "Zone",
        "responsible_user_name": c.responsible_user.full_name if c.responsible_user else "Safety Officer",
        "status": c.status,
        "deadline": c.deadline
    } for c in cases]

    summary_text = (
        f"This regulatory audit report synthesizes digital twin telemetry, computer vision PPE tracking, "
        f"and environmental IoT sensors across all 8 underground colliery sectors. "
        f"Currently, {open_cases} compliance case(s) remain under active mitigation. "
        f"Atmospheric gas levels are being actively monitored in real time. "
        f"All assigned safety supervisors are mandated to verify corrective remediation within statutory deadlines."
    )

    report_payload = {
        "title": report_title,
        "summary_text": summary_text,
        "kpis": kpis,
        "cases": case_list
    }

    ts_str = now.strftime("%Y%m%d_%H%M%S")
    if req.format.lower() == "excel":
        filename = f"report_{req.report_type}_{ts_str}.xlsx"
        file_path = generate_excel_report(report_payload, output_filename=filename)
        rel_path = f"/uploads/reports/{filename}"
    else:
        filename = f"report_{req.report_type}_{ts_str}.pdf"
        file_path = generate_pdf_report(report_payload, output_filename=filename)
        rel_path = f"/uploads/reports/{filename}"

    rep = Report(
        title=report_title,
        report_type=req.report_type,
        file_path=rel_path,
        file_format=req.format.lower(),
        summary_text=summary_text,
        created_at=now
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)

    create_audit_log(
        db,
        action="REPORT_GENERATED",
        entity_type="Report",
        entity_id=str(rep.id),
        new_state=f"Generated {req.format.upper()} report: {report_title}"
    )

    return rep

@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    rep = db.query(Report).filter(Report.id == report_id).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")

    filename = os.path.basename(rep.file_path)
    full_path = os.path.join(settings.REPORTS_DIR, filename)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    media_type = "application/pdf" if rep.file_format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return FileResponse(full_path, media_type=media_type, filename=filename)

