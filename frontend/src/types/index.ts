export interface Location {
  lat: number
  lon: number
}

export interface Observation {
  id: string
  latitude: number
  longitude: number
  timestamp: string
  photo_url: string | null
  water_clarity: string | null
  visible_waste: boolean | null
  algae: boolean | null
  odor: string | null
  created_at: string
}

export interface Evidence {
  id: string
  observation_id: string
  source_type: string
  timestamp: string
  location: Location | null
  payload: Record<string, any>
  quality_score: number
}

export interface Assessment {
  id: string
  observation_id: string
  assessment: string
  reliability: number
  confidence: number
  uncertainty: number
  requires_review: boolean
  explanation: string | null
}

export interface Scenario {
  scenario_id: string
  name: string
  description: string
  expected_status: string
}

export interface ScenarioRunResult {
  scenario_id: string
  observation_id: string
  assessment_id: string
  assessment: string
  evidence_status: string
  evidence_reliability: number
  assessment_confidence: number
  uncertainty: number
  requires_human_review: boolean
  supporting_evidence: string[]
  conflicting_evidence: string[]
  explanation: string
  recommended_action: string
  next_evidence: string | null
}

export interface Review {
  id: string
  assessment_id: string
  reviewer_decision: string
  reviewer_comment: string | null
  created_at: string
}
