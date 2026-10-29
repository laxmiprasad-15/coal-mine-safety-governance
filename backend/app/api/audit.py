from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditLog, Notification, User
from app.schemas.schemas import AuditLogResponse, NotificationResponse

router = APIRouter(prefix="/governance", tags=["Audit Trail & Notifications"])

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if action and action != "All":
        query = query.filter(AuditLog.action == action)
    if entity_type and entity_type != "All":
        query = query.filter(AuditLog.entity_type == entity_type)

    logs = query.limit(limit).all()
    results = []
    for l in logs:
        results.append(AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            user_name=l.user.full_name if l.user else "System Daemon",
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            previous_state=l.previous_state,
            new_state=l.new_state,
            ip_address=l.ip_address,
            tamper_token=l.tamper_token,
            timestamp=l.timestamp
        ))
    return results

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(unread_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Notification).order_by(Notification.created_at.desc())
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.limit(30).all()

@router.post("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.post("/notifications/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).update({Notification.is_read: True})
    db.commit()
    return {"message": "All notifications marked as read"}

