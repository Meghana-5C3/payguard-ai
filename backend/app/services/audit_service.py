from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models import AuditLog

class AuditService:
    def log_event(
        self,
        db: Session,
        evaluation_id: str,
        actor_type: str, # SYSTEM, CUSTOMER, ANALYST
        actor_id: str,
        action_taken: str,
        previous_state: str,
        new_state: str,
        notes: str = None
    ) -> AuditLog:
        log = AuditLog(
            evaluation_id=evaluation_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action_taken=action_taken,
            previous_state=previous_state,
            new_state=new_state,
            notes=notes,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

audit_service = AuditService()
