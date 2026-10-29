from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Contractor
from app.schemas.schemas import ContractorResponse

router = APIRouter(prefix="/contractors", tags=["Contractor Governance & Compliance"])

DEMO_CONTRACTORS = [
    {
        "name": "BGC Mining & Infra Pvt Ltd",
        "code": "CONT-BGC-01",
        "subsidiary": "BCCL",
        "work_order_no": "WO/BCCL/DHN/2026/041",
        "category": "OB Removal & Dump Maintenance",
        "active_workers": 42,
        "compliance_score": 94.5,
        "pme_valid": True,
        "vtc_trained": True,
        "insurance_active": True
    },
    {
        "name": "VPR Mining Infrastructure",
        "code": "CONT-VPR-02",
        "subsidiary": "ECL",
        "work_order_no": "WO/ECL/SNC/2026/118",
        "category": "Heavy Haulage & Dumper Operation",
        "active_workers": 68,
        "compliance_score": 88.0,
        "pme_valid": True,
        "vtc_trained": True,
        "insurance_active": True
    },
    {
        "name": "Thriveni Earthmovers Ltd",
        "code": "CONT-THRV-03",
        "subsidiary": "CCL",
        "work_order_no": "WO/CCL/RNC/2026/092",
        "category": "Deep Drill & Blasting Operations",
        "active_workers": 35,
        "compliance_score": 76.5,
        "pme_valid": False,  # 3 workers expired PME
        "vtc_trained": True,
        "insurance_active": True
    },
    {
        "name": "Kalinga Commercial Corporation",
        "code": "CONT-KCC-04",
        "subsidiary": "MCL",
        "work_order_no": "WO/MCL/SBP/2026/205",
        "category": "Coal Crushing & Feeder Maintenance",
        "active_workers": 28,
        "compliance_score": 91.0,
        "pme_valid": True,
        "vtc_trained": True,
        "insurance_active": True
    },
    {
        "name": "Dilip Buildcon Mining Division",
        "code": "CONT-DBL-05",
        "subsidiary": "NCL",
        "work_order_no": "WO/NCL/SNG/2026/310",
        "category": "Surface Dragline & Shovel Deployment",
        "active_workers": 54,
        "compliance_score": 83.0,
        "pme_valid": True,
        "vtc_trained": False, # VTC refresh due
        "insurance_active": True
    }
]

@router.get("/", response_model=List[ContractorResponse])
def get_all_contractors(subsidiary: Optional[str] = None, db: Session = Depends(get_db)):
    # Seed if empty
    if db.query(Contractor).count() == 0:
        for cdata in DEMO_CONTRACTORS:
            c = Contractor(
                name=cdata["name"],
                code=cdata["code"],
                subsidiary=cdata["subsidiary"],
                work_order_no=cdata["work_order_no"],
                category=cdata["category"],
                active_workers=cdata["active_workers"],
                compliance_score=cdata["compliance_score"],
                pme_valid=cdata["pme_valid"],
                vtc_trained=cdata["vtc_trained"],
                insurance_active=cdata["insurance_active"],
                valid_till=datetime.utcnow() + timedelta(days=180)
            )
            db.add(c)
        db.commit()

    query = db.query(Contractor)
    if subsidiary and subsidiary.upper() != "ALL":
        query = query.filter(Contractor.subsidiary == subsidiary.upper())
    return query.all()

@router.get("/summary")
def get_contractor_summary(db: Session = Depends(get_db)):
    contractors = db.query(Contractor).all()
    if not contractors:
        return {
            "total_contractors": 5,
            "total_contract_workers": 227,
            "avg_compliance_score": 86.6,
            "pme_compliant_rate": 80.0,
            "vtc_trained_rate": 80.0,
            "at_risk_contractors": 1
        }
    
    total = len(contractors)
    total_workers = sum(c.active_workers for c in contractors)
    avg_score = sum(c.compliance_score for c in contractors) / max(1, total)
    pme_ok = sum(1 for c in contractors if c.pme_valid)
    vtc_ok = sum(1 for c in contractors if c.vtc_trained)
    at_risk = sum(1 for c in contractors if c.compliance_score < 80.0)

    return {
        "total_contractors": total,
        "total_contract_workers": total_workers,
        "avg_compliance_score": round(avg_score, 1),
        "pme_compliant_rate": round((pme_ok / total) * 100, 1),
        "vtc_trained_rate": round((vtc_ok / total) * 100, 1),
        "at_risk_contractors": at_risk
    }
