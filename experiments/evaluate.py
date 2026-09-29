"""
AquaTrust Evaluation Script — controlled synthetic evaluation.

This is NOT a scientific validation. It evaluates the four deterministic
demo scenarios against expected outcomes using synthetic data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.conflict_engine import run_conflict_engine
from app.services.reliability_engine import run_reliability_engine
from app.services.assessment_engine import run_assessment_engine
from app.services.next_evidence_service import recommend_next_evidence
from app.services.demo_service import get_scenario


def evaluate_scenario(scenario_id: str) -> dict:
    """Evaluate a single scenario and return results."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        return {"scenario": scenario_id, "error": "Scenario not found"}

    obs = scenario["observation"]
    citizen = {
        "water_clarity": obs.get("water_clarity"),
        "visible_waste": obs.get("visible_waste"),
        "algae": obs.get("algae"),
        "odor": obs.get("odor"),
    }

    all_evidence = {"citizen": citizen}
    for ev in scenario["evidence"]:
        all_evidence[ev["source_type"]] = {
            **ev["payload"],
            "quality": ev.get("quality_score", 0.5),
            "timestamp": ev.get("timestamp"),
            "location": ev.get("location"),
        }

    # Run pipeline
    conflict_result = run_conflict_engine(citizen, all_evidence)
    reliability_result = run_reliability_engine(
        all_evidence,
        conflict_result["comparisons"],
        conflict_result["agreement_score"],
        conflict_result["evidence_status"],
    )
    assessment_label = run_assessment_engine(
        citizen,
        all_evidence,
        conflict_result["evidence_status"],
        reliability_result["confidence"],
    )
    next_evidence = recommend_next_evidence(
        citizen, all_evidence, conflict_result["comparisons"], conflict_result["evidence_status"]
    )

    expected = scenario["expected_status"]
    actual = conflict_result["evidence_status"]
    passed = expected == actual

    return {
        "scenario": scenario_id,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "confidence": reliability_result["confidence"],
        "reliability": reliability_result["reliability"],
        "uncertainty": reliability_result["uncertainty"],
        "review_required": reliability_result["requires_review"],
        "assessment": assessment_label,
        "next_evidence": next_evidence["recommended_action"],
        "next_evidence_priority": next_evidence["priority"],
        "conflicts_detected": len(conflict_result["conflicts"]),
        "supporting_evidence_count": len(conflict_result["supporting_evidence"]),
    }


def main():
    """Run evaluation for all four scenarios."""
    print("=" * 70)
    print("AquaTrust — Controlled Synthetic Evaluation")
    print("=" * 70)
    print()
    print("WARNING: This is a controlled synthetic evaluation using")
    print("deterministic demo scenarios. It is NOT a scientific validation.")
    print()

    scenario_ids = ["agreement", "citizen_conflict", "sensor_conflict", "missing_evidence"]
    results = []

    for sid in scenario_ids:
        result = evaluate_scenario(sid)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {sid}")
        print(f"       Expected: {result['expected']}")
        print(f"       Actual:   {result['actual']}")
        print(f"       Confidence: {result['confidence']:.0%}")
        print(f"       Reliability: {result['reliability']:.0%}")
        print(f"       Uncertainty: {result['uncertainty']:.0%}")
        print(f"       Review required: {result['review_required']}")
        print(f"       Next evidence: {result['next_evidence']} ({result['next_evidence_priority']})")
        print()

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pass_rate = passed / total if total > 0 else 0

    print("-" * 70)
    print(f"Results: {passed}/{total} scenarios passed ({pass_rate:.0%})")
    print("-" * 70)
    print()
    print("Metrics:")
    print(f"  - Conflict detection: {sum(1 for r in results if r['conflicts_detected'] > 0)}/{total} scenarios with conflicts detected")
    print(f"  - Review triggering: {sum(1 for r in results if r['review_required'])}/{total} scenarios require review")
    print(f"  - Avg confidence: {sum(r['confidence'] for r in results) / total:.0%}")
    print(f"  - Avg reliability: {sum(r['reliability'] for r in results) / total:.0%}")
    print()
    print("NOTE: These metrics are based on synthetic demo data only.")
    print("They do not represent real-world performance.")

    # Machine-readable output
    print()
    print("=" * 70)
    print("Machine-readable results (JSON):")
    print("=" * 70)
    import json
    print(json.dumps({
        "evaluation_type": "controlled_synthetic",
        "total_scenarios": total,
        "passed": passed,
        "pass_rate": pass_rate,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
