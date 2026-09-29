import type { ScenarioRunResult } from '../../types'

interface Props {
  result: ScenarioRunResult
  onNext: () => void
}

export default function ConflictPanel({ result, onNext }: Props) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Why did AquaTrust reach this assessment?
        </h2>

        {/* Explanation */}
        <div className="bg-slate-50 rounded-lg p-4 mb-6">
          <p className="text-slate-700 leading-relaxed">{result.explanation}</p>
        </div>

        {/* Supporting Evidence */}
        {result.supporting_evidence.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-green-700 uppercase tracking-wide mb-3">
              Supporting Evidence
            </h3>
            <ul className="space-y-2">
              {result.supporting_evidence.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Conflicting Evidence */}
        {result.conflicting_evidence.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-red-700 uppercase tracking-wide mb-3">
              Conflicting Evidence
            </h3>
            <ul className="space-y-2">
              {result.conflicting_evidence.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-red-500 mt-0.5">⚠</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={onNext}
          className="bg-aqua-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-aqua-700 transition"
        >
          View Action →
        </button>
      </div>
    </div>
  )
}
