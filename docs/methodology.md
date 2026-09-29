# AquaTrust Methodology

## Research Design

AquaTrust evaluates whether cross-source evidence verification can improve the reliability of citizen-generated freshwater observations while preserving human oversight.

## Core Methodology

### 1. Evidence Alignment

Each evidence source is aligned against the citizen observation using three dimensions:

**Spatial Alignment** — Haversine distance between evidence location and observation location:
```
spatial_score = 1.0 - (distance_km / threshold_km)
```
Where `threshold_km = 5.0` (configurable). Score ranges 0.0–1.0.

**Temporal Alignment** — Time difference between evidence timestamp and observation timestamp:
```
temporal_score = 1.0 - (diff_hours / threshold_hours)
```
Where `threshold_hours = 24.0` (configurable). Score ranges 0.0–1.0.

**Source Quality** — Quality score provided by the evidence source (0.0–1.0).

**Overall Alignment** — Weighted combination:
```
alignment_score = 0.35 * spatial + 0.25 * temporal + 0.40 * quality
```

### 2. Conflict Detection

The conflict engine compares citizen observations against each evidence source using a deterministic signal mapping:

| Citizen Observation | Expected Sensor Signal |
|---------------------|----------------------|
| clear | turbidity ≤ 5 NTU |
| slightly_cloudy | turbidity 5–25 NTU |
| cloudy | turbidity 25–50 NTU |
| opaque | turbidity > 50 NTU |

Each comparison produces a relationship:
- **AGREEMENT** — Evidence supports citizen observation
- **PARTIAL** — Evidence partially supports
- **CONFLICT** — Evidence contradicts citizen observation
- **MISSING** — Evidence unavailable

Overall evidence status:
- **SUPPORTED** — Multiple independent sources agree
- **PARTIALLY_SUPPORTED** — Some agreement, some conflict
- **CONTRADICTED** — Sources contradict citizen observation
- **INSUFFICIENT_EVIDENCE** — Not enough evidence for assessment

### 3. Reliability Calculation

Evidence reliability measures how trustworthy the available evidence is:

```
reliability = 0.30 * avg_quality
            + 0.20 * count_factor
            + 0.15 * diversity_factor
            + 0.35 * avg_agreement
```

Where:
- `avg_quality` — average quality score across all sources
- `count_factor` — min(source_count / 4, 1.0)
- `diversity_factor` — min(source_type_count / 4, 1.0)
- `avg_agreement` — average agreement score from comparisons

### 4. Confidence Calculation

Assessment confidence measures how strongly the evidence supports the final assessment:

```
base_confidence = 0.5 * agreement_score + 0.5 * reliability
confidence = base_confidence * status_multiplier
```

Status multipliers:
| Status | Multiplier |
|--------|-----------|
| SUPPORTED | 1.0 |
| PARTIALLY_SUPPORTED | 0.75 |
| UNCERTAIN | 0.5 |
| CONTRADICTED | 0.3 |
| INSUFFICIENT_EVIDENCE | 0.2 |

### 5. Uncertainty Calculation

```
uncertainty = (1.0 - confidence)
            + min(conflict_count * 0.1, 0.3)
            + min(missing_count * 0.15, 0.3)
```

### 6. Human Review Triggering

Human review is required when:
- Evidence status is `CONTRADICTED` or `INSUFFICIENT_EVIDENCE`
- Confidence < 0.5
- Uncertainty > 0.6

## Evaluation Methodology

The evaluation uses **controlled synthetic data** — four deterministic scenarios with known expected outcomes. This is NOT a scientific validation.

### Scenarios

1. **Agreement** — All sources support the observation → Expected: `SUPPORTED`
2. **Citizen Conflict** — Sources contradict the observation → Expected: `CONTRADICTED`
3. **Sensor Conflict** — Mixed evidence → Expected: `PARTIALLY_SUPPORTED`
4. **Missing Evidence** — Insufficient data → Expected: `INSUFFICIENT_EVIDENCE`

### Metrics

- Conflict detection accuracy (expected vs actual status)
- Confidence calibration (confidence should be lower for conflicting scenarios)
- Review triggering (review required for conflicting/insufficient scenarios)
- Next evidence recommendation appropriateness

## Limitations

- **Synthetic data only** — No real-world validation performed
- **Simple signal mapping** — Real water quality is more complex
- **No temporal dynamics** — Does not model seasonal or trend changes
- **Prototype metrics** — Reliability and confidence are not scientifically validated
- **Limited evidence types** — Only five source types supported

## Future Methodology Improvements

- Real-world validation with certified sensor data
- Bayesian reliability modeling
- Temporal trend analysis
- Seasonal baseline adjustment
- Multi-location spatial interpolation
