from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import PolicyRule
from backend.app.schemas import PolicyRuleCreateSchema, PolicyRuleResponseSchema
from backend.app.services.policy_engine import policy_engine, DEFAULT_POLICIES

router = APIRouter(prefix="/api/v1/policies", tags=["Policy Engine"])

@router.get("", response_model=List[PolicyRuleResponseSchema])
def list_policies(db: Session = Depends(get_db)):
    policy_engine.seed_default_policies(db)
    rules = db.query(PolicyRule).order_by(PolicyRule.priority.asc()).all()
    return [
        PolicyRuleResponseSchema(
            id=r.id,
            rule_name=r.rule_name,
            description=r.description,
            priority=r.priority,
            condition_json=r.condition_json,
            action=r.action,
            is_active=r.is_active,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in rules
    ]

@router.post("", response_model=PolicyRuleResponseSchema)
def create_policy(payload: PolicyRuleCreateSchema, db: Session = Depends(get_db)):
    rule = PolicyRule(
        rule_name=payload.rule_name,
        description=payload.description,
        priority=payload.priority,
        condition_json=payload.condition_json,
        action=payload.action,
        is_active=payload.is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return PolicyRuleResponseSchema(
        id=rule.id,
        rule_name=rule.rule_name,
        description=rule.description,
        priority=rule.priority,
        condition_json=rule.condition_json,
        action=rule.action,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat()
    )

@router.put("/{rule_id}", response_model=PolicyRuleResponseSchema)
def update_policy(rule_id: str, payload: PolicyRuleCreateSchema, db: Session = Depends(get_db)):
    rule = db.query(PolicyRule).filter(PolicyRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Policy rule not found.")

    rule.rule_name = payload.rule_name
    rule.description = payload.description
    rule.priority = payload.priority
    rule.condition_json = payload.condition_json
    rule.action = payload.action
    rule.is_active = payload.is_active
    rule.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(rule)
    return PolicyRuleResponseSchema(
        id=rule.id,
        rule_name=rule.rule_name,
        description=rule.description,
        priority=rule.priority,
        condition_json=rule.condition_json,
        action=rule.action,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat()
    )

@router.post("/reset-defaults")
def reset_default_policies(db: Session = Depends(get_db)):
    db.query(PolicyRule).delete()
    db.commit()
    policy_engine.seed_default_policies(db)
    return {"status": "SUCCESS", "message": "Policy rules reset to default baseline."}
