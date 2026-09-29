# AquaTrust Research Documentation

## Research Question

> Can cross-source evidence verification improve the reliability of citizen-generated freshwater ecosystem observations while preserving human oversight?

## Track 3 Alignment: AI-Supported Assessment

AquaTrust aligns with Track 3 by demonstrating how AI can **assess** the reliability of citizen observations without replacing human judgment. The system:

1. **Does NOT predict water quality** — it validates citizen observations against evidence
2. **Does NOT replace humans** — it triggers human review when evidence is insufficient
3. **Does NOT use opaque AI** — all calculations are deterministic and inspectable
4. **DOES improve reliability** — cross-source verification catches conflicts and gaps

## Research Contribution

The core research contribution is an **evidence-aware validation framework** that:

- Accepts citizen observations as input
- Collects evidence from multiple independent sources
- Aligns evidence spatially and temporally
- Detects agreement and conflict deterministically
- Separates evidence reliability from assessment confidence
- Explains every assessment with supporting/conflicting evidence
- Triggers human review when appropriate
- Recommends next evidence collection actions

## Key Research Insights

### 1. Reliability ≠ Confidence

Evidence reliability measures the **trustworthiness of the evidence itself**. Assessment confidence measures **how strongly the evidence supports the conclusion**. These are fundamentally different and must be calculated separately.

### 2. Conflict Detection Must Be Deterministic

Using an LLM for conflict detection would make the system a black box. Deterministic rules make every decision traceable, explainable, and modifiable.

### 3. Human-in-the-Loop is Essential

The system must know when it doesn't know. When evidence is insufficient or conflicting, the system should explicitly flag this and request human review rather than producing a potentially misleading assessment.

### 4. Next Evidence Recommendations Improve Efficiency

Rather than just saying "insufficient evidence", the system should recommend **what specific evidence** would be most valuable to collect next.

## Related Work

- **Citizen science validation** — Traditional approaches rely on expert review of every observation
- **Sensor fusion** — Combining multiple sensor readings, but typically not with citizen observations
- **Uncertainty quantification** — Important for environmental monitoring, but often opaque
- **Explainable AI** — Critical for environmental decision-making systems

## Evaluation Approach

The evaluation uses **controlled synthetic scenarios** with known expected outcomes. This allows us to verify that the system produces correct results for well-defined cases.

### What We Evaluate

- Conflict detection correctness
- Confidence calibration (lower confidence for conflicting scenarios)
- Review triggering (review required when appropriate)
- Next evidence recommendation appropriateness

### What We Do NOT Claim

- Scientific validity
- Regulatory compliance
- Real-world performance
- Superiority over existing systems

## Future Research Directions

1. **Real-world validation** — Partner with citizen science organizations to test with real data
2. **Bayesian reliability modeling** — More sophisticated uncertainty quantification
3. **Temporal dynamics** — Model seasonal and trend changes in water quality
4. **Spatial interpolation** — Estimate conditions between observation points
5. **Adaptive evidence collection** — Learn which evidence types are most valuable for different scenarios
6. **Multi-stakeholder review** — Different review workflows for different user roles

## Ethical Considerations

- **Transparency** — All calculations are inspectable and explainable
- **Human oversight** — The system assists rather than replaces human judgment
- **Data quality** — Demo data is clearly labeled as synthetic
- **No false precision** — Confidence is presented as a prototype metric, not scientific certainty
- **Accessibility** — The system is designed to be understandable by non-experts
