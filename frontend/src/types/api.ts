export interface TransactionPayload {
  user_id: string;
  merchant_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  device_fingerprint: string;
  ip_address: string;
  geo_location: string;
  lat?: number;
  lon?: number;
}

export interface ShapAttribution {
  feature: string;
  label: string;
  value: any;
  impact: string;
  raw_shap_value: number;
  direction: 'INCREASES_RISK' | 'REDUCES_RISK';
  description: string;
}

export interface PolicyTrigger {
  rule_id: string;
  rule_name: string;
  action: 'APPROVE' | 'VERIFY' | 'HOLD';
  description: string;
}

export interface RiskEvaluationResponse {
  transaction_id: string;
  evaluated_at: string;
  model_version: string;
  risk_score: number;
  raw_probability: number;
  calibrated_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommended_action: 'APPROVE' | 'VERIFY' | 'HOLD';
  challenge_token?: string;
  status: string;
  explanations: ShapAttribution[];
  policy_triggers: PolicyTrigger[];
  natural_explanation: string;
}

export interface AnalystQueueItem {
  evaluation_id: string;
  transaction_id: string;
  evaluated_at: string;
  amount: number;
  currency: string;
  payment_method: string;
  user_id: string;
  user_email: string;
  merchant_name: string;
  merchant_mcc_tier: number;
  risk_score: number;
  calibrated_probability: number;
  raw_probability: number;
  decision_action: string;
  status: string;
  device_fingerprint: string;
  ip_address: string;
  geo_location: string;
  shap_attributions: ShapAttribution[];
  triggered_policy_rules: PolicyTrigger[];
  natural_explanation: string;
  analyst_notes?: string;
}

export interface PolicyRule {
  id: string;
  rule_name: string;
  description: string;
  priority: number;
  condition_json: any;
  action: 'APPROVE' | 'VERIFY' | 'HOLD';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuditLogItem {
  id: string;
  evaluation_id: string;
  transaction_id: string;
  actor_type: 'SYSTEM' | 'CUSTOMER' | 'ANALYST';
  actor_id: string;
  action_taken: string;
  previous_state?: string;
  new_state: string;
  notes?: string;
  timestamp: string;
}

export interface CalibrationBin {
  bin_lower: number;
  bin_upper: number;
  count: number;
  actual_rate: number;
  predicted_prob: number;
}

export interface FeatureImportance {
  feature: string;
  label: string;
  importance: number;
}

export interface ModelMetricsResponse {
  model_type: string;
  n_train: number;
  n_test: number;
  fraud_prevalence: number;
  roc_auc: number;
  brier_score_raw: number;
  brier_score_calibrated: number;
  ece_raw: number;
  ece_calibrated: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  calibration_curve: CalibrationBin[];
  global_feature_importance: FeatureImportance[];
  feature_names: string[];
  feature_labels: Record<string, string>;
}

// Public Benchmark Types
export interface PublicPredictionPayload {
  Time: number;
  V1: number; V2: number; V3: number; V4: number; V5: number;
  V6: number; V7: number; V8: number; V9: number; V10: number;
  V11: number; V12: number; V13: number; V14: number; V15: number;
  V16: number; V17: number; V18: number; V19: number; V20: number;
  V21: number; V22: number; V23: number; V24: number; V25: number;
  V26: number; V27: number; V28: number;
  Amount: number;
  include_explanations?: boolean;
}

export interface PublicShapAttribution {
  feature: string;
  feature_type: string;
  feature_value: number;
  shap_value: number;
  direction: string;
}

export interface PublicPredictionResponse {
  model_version: string;
  dataset_source: string;
  dataset_type: string;
  raw_probability: number;
  calibrated_probability: number;
  threshold: number;
  threshold_source: string;
  calibration_method: string;
  decision: string;
  top_positive_features?: PublicShapAttribution[];
  top_negative_features?: PublicShapAttribution[];
}
