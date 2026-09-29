# AquaTrust — Features

## Core Features

### 1. Citizen Observation Submission

Citizens can submit structured freshwater observations:

| Field | Type | Options |
|-------|------|---------|
| Location | lat/lon | Any valid coordinates |
| Timestamp | ISO 8601 | Defaults to now |
| Water Clarity | enum | clear, slightly_cloudy, cloudy, opaque |
| Visible Waste | boolean | yes/no |
| Algae | boolean | yes/no |
| Odor | enum | none, earthy, chemical, sewage |
| Photo | URL | Optional |

**API**: `POST /api/observations`

---

### 2. Multi-Source Evidence Collection

Evidence from five independent source types:

| Source | Type | Key Measurements |
|--------|------|-----------------|
| Citizen | `citizen` | water_clarity, visible_waste, algae, odor |
| Sensor | `sensor` | turbidity, ph, conductivity, temperature |
| Satellite | `satellite` | anomaly_score, ndvi, cloud_cover |
| Weather | `weather` | rainfall_mm, temperature, wind_speed |
| Historical | `historical` | baseline_normal, turbidity, seasonal_norm |

Each evidence source is stored independently with its own quality score.

**API**: `POST /api/evidence`

---

### 3. Evidence Alignment

Deterministic spatial, temporal, and quality alignment:

```
spatial_score  = 1.0 - (distance_km / 5.0)        # 0.0–1.0
temporal_score = 1.0 - (diff_hours / 24.0)         # 0.0–1.0
alignment_score = 0.35*spatial + 0.25*temporal + 0.40*quality
```

All scores are **prototype metrics**, not scientifically validated.

---

### 4. Conflict Detection

Deterministic conflict engine with four statuses:

| Status | Meaning |
|--------|---------|
| `SUPPORTED` | Multiple independent sources support the observation |
| `PARTIALLY_SUPPORTED` | Some sources support, some conflict |
| `CONTRADICTED` | Sources contradict the observation |
| `INSUFFICIENT_EVIDENCE` | Not enough evidence for assessment |

Every conflict identifies the source pair:
```json
{
  "source_a": "citizen",
  "source_b": "sensor",
  "relationship": "CONFLICT",
  "agreement_score": 0.31,
  "explanation": "Citizen reports cloudy water but sensor shows low turbidity"
}
```

---

### 5. Reliability vs Confidence

Two separate, clearly distinguished metrics:

**Evidence Reliability** — How trustworthy is the evidence?
```
reliability = 0.30*avg_quality + 0.20*count_factor + 0.15*diversity + 0.35*agreement
```

**Assessment Confidence** — How strongly does evidence support the conclusion?
```
confidence = (0.5*agreement + 0.5*reliability) * status_multiplier
```

---

### 6. Human-in-the-Loop Review

Automatic review triggering when:
- Evidence status is `CONTRADICTED` or `INSUFFICIENT_EVIDENCE`
- Confidence < 50%
- Uncertainty > 60%

Reviewer actions:
- **Approve** — Confirm the assessment
- **Reject** — Reject the assessment
- **Needs More Evidence** — Request additional data
- **Comment** — Add review notes

Original AI assessment is always preserved. Reviews stored as separate provenance events.

**API**: `POST /api/reviews`

---

### 7. Next Best Evidence Recommendations

Deterministic rule-based recommendations:

| Condition | Recommendation | Priority |
|-----------|---------------|----------|
| Sensor missing | Collect sensor/turbidity measurement | HIGH |
| Citizen vs sensor conflict | Repeat turbidity measurement | HIGH |
| Multiple sources conflict | Request human review | HIGH |
| Insufficient evidence | Collect additional independent evidence | HIGH |
| Satellite missing | Collect satellite imagery | MEDIUM |
| Historical missing | Collect historical baseline data | MEDIUM |
| Weather missing | Collect weather/rainfall data | LOW |
| Low quality photo | Request clearer photo | MEDIUM |

---

### 8. Explainable Assessments

Every assessment includes:

1. **What** — The assessment label
2. **Why** — Human-readable explanation
3. **Supporting evidence** — List of supporting sources
4. **Conflicting evidence** — List of conflicting sources
5. **Uncertainty** — How uncertain the system is
6. **Next step** — Recommended action

---

### 9. Demo Scenarios

Four deterministic scenarios for hackathon demonstration:

| Scenario | Description | Expected Status |
|----------|-------------|-----------------|
| Agreement | Citizen cloudy + sensor high turbidity + satellite anomaly | `SUPPORTED` |
| Citizen Conflict | Citizen opaque + sensor normal + satellite no anomaly | `CONTRADICTED` |
| Sensor Conflict | Citizen cloudy + sensor normal + satellite anomaly | `PARTIALLY_SUPPORTED` |
| Missing Evidence | Citizen cloudy + no sensor + satellite unclear | `INSUFFICIENT_EVIDENCE` |

**API**:
- `GET /api/demo/scenarios` — List all scenarios
- `GET /api/demo/scenarios/{id}` — Get scenario definition
- `POST /api/demo/scenarios/{id}/run` — Run scenario end-to-end

---

### 10. Evaluation Framework

Controlled synthetic evaluation:

```bash
cd backend
python ../experiments/evaluate.py
```

Reports:
- Conflict detection accuracy
- Confidence calibration
- Review triggering
- Next evidence recommendations
- Machine-readable JSON output

**Note**: This is a controlled synthetic evaluation, NOT a scientific validation.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/observations` | POST | Create observation |
| `/api/observations/{id}` | GET | Get observation |
| `/api/observations` | GET | List observations |
| `/api/evidence` | POST | Submit evidence |
| `/api/evidence/{observation_id}` | GET | Get evidence for observation |
| `/api/assessments/{observation_id}` | POST | Run assessment |
| `/api/assessments/{observation_id}` | GET | Get latest assessment |
| `/api/assessments/{observation_id}/explanation` | GET | Get explanation |
| `/api/observations/{id}/next-evidence` | GET | Get next evidence recommendation |
| `/api/reviews` | POST | Submit human review |
| `/api/reviews/{id}` | GET | Get review |
| `/api/demo/scenarios` | GET | List demo scenarios |
| `/api/demo/scenarios/{id}` | GET | Get scenario definition |
| `/api/demo/scenarios/{id}/run` | POST | Run scenario end-to-end |

---

## Frontend Features

### Observation Screen
- Structured form with all observation fields
- Demo scenario selector for quick reproduction

### Evidence Screen
- Separate cards for each evidence source
- Source-specific display (sensor measurements, satellite anomaly, etc.)
- Quality/reliability indicators

### Assessment Screen
- Large assessment label
- Evidence reliability, assessment confidence, uncertainty
- Evidence status badge
- Human review indicator

### Explanation Screen
- "Why did AquaTrust reach this assessment?"
- Supporting evidence list
- Conflicting evidence list

### Action Screen
- Recommended next step with reason
- Request Human Review button
- Review submission form (approve/reject/modify)

---

## What AquaTrust Does NOT Do

- Does NOT predict water quality
- Does NOT replace human judgment
- Does NOT use opaque AI for decisions
- Does NOT claim scientific validation
- Does NOT claim regulatory compliance
- Does NOT fabricate real sensor/satellite data
- Does NOT require PostgreSQL for demo
- Does NOT depend on live external APIs
