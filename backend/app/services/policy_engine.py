import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models import PolicyRule, FeatureVector

DEFAULT_POLICIES = [
    {
        "rule_name": "Critical Risk Score Escalation",
        "description": "Automatically escalate transactions with calibrated risk score >= 850 to Analyst Review Queue (HOLD).",
        "priority": 1,
        "action": "HOLD",
        "condition_json": {"operator": "AND", "rules": [{"field": "risk_score", "op": ">=", "value": 850}]},
        "is_active": True
    },
    {
        "rule_name": "High Velocity & New Device Challenge",
        "description": "Trigger 2FA verification challenge if 1-hour velocity > 2 and device fingerprint is unrecognized.",
        "priority": 2,
        "action": "VERIFY",
        "condition_json": {
            "operator": "AND",
            "rules": [
                {"field": "tx_velocity_1h", "op": ">=", "value": 3},
                {"field": "is_new_device", "op": "==", "value": 1}
            ]
        },
        "is_active": True
    },
    {
        "rule_name": "Suspicious Amount & Proxy IP Challenge",
        "description": "Trigger 2FA challenge if Z-score > 2.5 and IP reputation risk score > 70.",
        "priority": 3,
        "action": "VERIFY",
        "condition_json": {
            "operator": "AND",
            "rules": [
                {"field": "tx_amount_zscore", "op": ">=", "value": 2.5},
                {"field": "ip_reputation_score", "op": ">=", "value": 70.0}
            ]
        },
        "is_active": True
    },
    {
        "rule_name": "Moderate Risk Verification Threshold",
        "description": "Require verification for transactions with risk score between 650 and 849.",
        "priority": 4,
        "action": "VERIFY",
        "condition_json": {
            "operator": "AND",
            "rules": [
                {"field": "risk_score", "op": ">=", "value": 650},
                {"field": "risk_score", "op": "<", "value": 850}
            ]
        },
        "is_active": True
    },
    {
        "rule_name": "Standard Approval Rule",
        "description": "Approve transactions with low risk score (< 650) and normal operational parameters.",
        "priority": 10,
        "action": "APPROVE",
        "condition_json": {"operator": "AND", "rules": [{"field": "risk_score", "op": "<", "value": 650}]},
        "is_active": True
    }
]

class PolicyEngine:
    def seed_default_policies(self, db: Session):
        existing_count = db.query(PolicyRule).count()
        if existing_count == 0:
            print("[PolicyEngine] Seeding default adaptive policy rules...")
            for pol in DEFAULT_POLICIES:
                rule = PolicyRule(
                    rule_name=pol["rule_name"],
                    description=pol["description"],
                    priority=pol["priority"],
                    action=pol["action"],
                    condition_json=pol["condition_json"],
                    is_active=pol["is_active"]
                )
                db.add(rule)
            db.commit()

    def evaluate(self, db: Session, fv: FeatureVector, risk_score: int) -> Tuple[str, List[Dict[str, Any]]]:
        self.seed_default_policies(db)

        active_rules = db.query(PolicyRule).filter(PolicyRule.is_active == True).order_by(PolicyRule.priority.asc()).all()

        context = {
            "amount": fv.amount,
            "tx_amount_zscore": fv.tx_amount_zscore,
            "tx_velocity_1h": fv.tx_velocity_1h,
            "tx_velocity_24h": fv.tx_velocity_24h,
            "tx_amount_sum_24h": fv.tx_amount_sum_24h,
            "is_new_device": fv.is_new_device,
            "is_cross_border": fv.is_cross_border,
            "time_since_last_tx_sec": fv.time_since_last_tx_sec,
            "distance_from_home_km": fv.distance_from_home_km,
            "mcc_risk_tier": fv.mcc_risk_tier,
            "ip_reputation_score": fv.ip_reputation_score,
            "failed_otp_attempts_24h": fv.failed_otp_attempts_24h,
            "risk_score": risk_score
        }

        triggered_triggers = []
        final_action = "APPROVE"

        for rule in active_rules:
            if self._eval_condition_group(rule.condition_json, context):
                triggered_triggers.append({
                    "rule_id": rule.id,
                    "rule_name": rule.rule_name,
                    "action": rule.action,
                    "description": rule.description
                })
                # First matching highest priority rule determines action (precedence: HOLD > VERIFY > APPROVE)
                if rule.action == "HOLD":
                    final_action = "HOLD"
                    break
                elif rule.action == "VERIFY" and final_action != "HOLD":
                    final_action = "VERIFY"

        return final_action, triggered_triggers

    def _eval_condition_group(self, group: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
        op = group.get("operator", "AND").upper()
        rules = group.get("rules", [])

        results = []
        for r in rules:
            if "operator" in r:
                res = self._eval_condition_group(r, ctx)
            else:
                res = self._eval_single_rule(r, ctx)
            results.append(res)

        if not results:
            return False

        if op == "AND":
            return all(results)
        elif op == "OR":
            return any(results)
        return False

    def _eval_single_rule(self, rule: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
        field = rule.get("field")
        op = rule.get("op")
        target_val = rule.get("value")

        actual_val = ctx.get(field)
        if actual_val is None:
            return False

        if op == "==":
            return actual_val == target_val
        elif op == "!=":
            return actual_val != target_val
        elif op == ">":
            return actual_val > target_val
        elif op == ">=":
            return actual_val >= target_val
        elif op == "<":
            return actual_val < target_val
        elif op == "<=":
            return actual_val <= target_val
        return False

policy_engine = PolicyEngine()
