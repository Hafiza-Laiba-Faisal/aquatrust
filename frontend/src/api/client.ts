import type { Observation, Evidence, Assessment, Scenario, ScenarioRunResult, Review } from '../types'

const API_BASE = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Observations
  createObservation: (data: Partial<Observation>) =>
    fetchJson<Observation>('/observations', { method: 'POST', body: JSON.stringify(data) }),

  getObservation: (id: string) =>
    fetchJson<Observation>(`/observations/${id}`),

  // Evidence
  createEvidence: (data: Partial<Evidence>) =>
    fetchJson<Evidence>('/evidence', { method: 'POST', body: JSON.stringify(data) }),

  getEvidence: (observationId: string) =>
    fetchJson<Evidence[]>(`/evidence/${observationId}`),

  // Assessments
  createAssessment: (observationId: string) =>
    fetchJson<Assessment>(`/assessments/${observationId}`, { method: 'POST' }),

  getAssessment: (observationId: string) =>
    fetchJson<Assessment>(`/assessments/${observationId}`),

  getNextEvidence: (observationId: string) =>
    fetchJson<{ next_evidence: string }>(`/observations/${observationId}/next-evidence`),

  // Reviews
  createReview: (data: { assessment_id: string; reviewer_decision: string; reviewer_comment?: string }) =>
    fetchJson<Review>('/reviews', { method: 'POST', body: JSON.stringify(data) }),

  getReview: (id: string) =>
    fetchJson<Review>(`/reviews/${id}`),

  // Demo scenarios
  getScenarios: () =>
    fetchJson<{ scenarios: Scenario[] }>('/demo/scenarios'),

  getScenario: (id: string) =>
    fetchJson<Scenario>(`/demo/scenarios/${id}`),

  runScenario: (id: string) =>
    fetchJson<ScenarioRunResult>(`/demo/scenarios/${id}/run`, { method: 'POST' }),
}
