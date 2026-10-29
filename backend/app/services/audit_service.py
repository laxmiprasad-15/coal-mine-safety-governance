import hashlib
import json
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog

def create_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str = None,
    user_id: int = None,
    previous_state: Any = None,
    new_state: Any = None,
    ip_address: str = "127.0.0.1"
) -> AuditLog:
    """
    Creates an immutable audit trail entry with a cryptographic SHA-256 tamper verification hash.
    """
    prev_str = json.dumps(previous_state, default=str) if previous_state is not None else None
    new_str = json.dumps(new_state, default=str) if new_state is not None else None
    now_ts = datetime.utcnow()

    # Form cryptographic hash chaining user, action, timestamp and state delta
    raw_hash_payload = f"{user_id}:{action}:{entity_type}:{entity_id}:{prev_str}:{new_str}:{now_ts.isoformat()}"
    tamper_token = hashlib.sha256(raw_hash_payload.encode('utf-8')).hexdigest()

    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        previous_state=prev_str,
        new_state=new_str,
        ip_address=ip_address,
        tamper_token=tamper_token,
        timestamp=now_ts
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
