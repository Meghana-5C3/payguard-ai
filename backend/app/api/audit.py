from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AuditLog, RiskEvaluation, Transaction
from backend.app.schemas import AuditLogResponseSchema

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Trail"])

@router.get("/logs", response_model=List[AuditLogResponseSchema])
def get_audit_logs(
    evaluation_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if evaluation_id:
        query = query.filter(AuditLog.evaluation_id == evaluation_id)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    result = []
    for log in logs:
        ev = db.query(RiskEvaluation).filter(RiskEvaluation.id == log.evaluation_id).first()
        tx_id = ev.transaction_id if ev else "UNKNOWN"

        result.append(AuditLogResponseSchema(
            id=log.id,
            evaluation_id=log.evaluation_id,
            transaction_id=tx_id,
            actor_type=log.actor_type,
            actor_id=log.actor_id,
            action_taken=log.action_taken,
            previous_state=log.previous_state,
            new_state=log.new_state,
            notes=log.notes,
            timestamp=log.timestamp.isoformat()
        ))

    return result
