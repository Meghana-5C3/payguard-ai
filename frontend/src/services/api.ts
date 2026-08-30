import axios from 'axios';
import {
  TransactionPayload,
  RiskEvaluationResponse,
  AnalystQueueItem,
  PolicyRule,
  AuditLogItem,
  ModelMetricsResponse,
  PublicPredictionPayload,
  PublicPredictionResponse
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const PUBLIC_API_URL = import.meta.env.VITE_PUBLIC_API_URL || '/api/public';

export const api = {
  evaluateTransaction: async (payload: TransactionPayload): Promise<RiskEvaluationResponse> => {
    const res = await axios.post(`${API_BASE_URL}/risk/evaluate`, payload);
    return res.data;
  },

  predictPublicBenchmark: async (payload: PublicPredictionPayload): Promise<PublicPredictionResponse> => {
    const res = await axios.post(`${PUBLIC_API_URL}/predict`, payload);
    return res.data;
  },

  verifyChallenge: async (transactionId: string, challengeToken: string, otpCode: string) => {
    const res = await axios.post(`${API_BASE_URL}/risk/verify`, {
      transaction_id: transactionId,
      challenge_token: challengeToken,
      otp_code: otpCode
    });
    return res.data;
  },

  getAnalystQueue: async (statusFilter = 'ALL'): Promise<AnalystQueueItem[]> => {
    const res = await axios.get(`${API_BASE_URL}/analyst/queue`, {
      params: { status_filter: statusFilter }
    });
    return res.data;
  },

  submitAnalystOverride: async (evaluationId: string, action: 'APPROVE' | 'REJECT', reasonCode: string, notes: string) => {
    const res = await axios.post(`${API_BASE_URL}/analyst/override`, {
      evaluation_id: evaluationId,
      override_action: action,
      reason_code: reasonCode,
      analyst_notes: notes
    });
    return res.data;
  },

  getPolicies: async (): Promise<PolicyRule[]> => {
    const res = await axios.get(`${API_BASE_URL}/policies`);
    return res.data;
  },

  updatePolicy: async (ruleId: string, policyData: Partial<PolicyRule>): Promise<PolicyRule> => {
    const res = await axios.put(`${API_BASE_URL}/policies/${ruleId}`, policyData);
    return res.data;
  },

  resetPolicies: async () => {
    const res = await axios.post(`${API_BASE_URL}/policies/reset-defaults`);
    return res.data;
  },

  getMetrics: async (): Promise<ModelMetricsResponse> => {
    const res = await axios.get(`${API_BASE_URL}/metrics/performance`);
    return res.data;
  },

  getAuditLogs: async (): Promise<AuditLogItem[]> => {
    const res = await axios.get(`${API_BASE_URL}/audit/logs`);
    return res.data;
  }
};
