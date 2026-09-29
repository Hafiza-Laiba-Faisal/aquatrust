import type { ScenarioRunResult } from '../../types'

interface Props {
  result: ScenarioRunResult
  onNext: () => void
}

export default function ConfidenceCard({ result, onNext }: Props) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUPPORTED': return 'bg-green-100 text-green-800'
      case 'PARTIALLY_SUPPORTED': return 'bg-amber-100 text-amber-800'
      case 'CONTRADICTED': return 'bg-red-100 text-red-800'
      case 'INSUFFICIENT_EVIDENCE': return 'bg-slate-100 text-slate-800'
      default: return 'bg-slate-100 text-slate-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Main Assessment Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
        <div className="text-sm text-slate-500 uppercase tracking-wide mb-2">Assessment</div>
        <h2 className="text-3xl font-bold text-slate-800 mb-6">{result.assessment}</h2>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div>
            <div className="text-sm text-slate-500 mb-1">Evidence Reliability</div>
            <div className="text-2xl font-bold text-aqua-700">
              {Math.round(result.evidence_reliability * 100)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-slate-500 mb-1">Assessment Confidence</div>
            <div className="text-2xl font-bold text-aqua-700">
              {Math.round(result.assessment_confidence * 100)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-slate-500 mb-1">Uncertainty</div>
            <div className="text-2xl font-bold text-amber-600">
              {Math.round(result.uncertainty * 100)}%
            </div>
          </div>
        </div>

        <div className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(result.evidence_status)}`}>
          {result.evidence_status.replace(/_/g, ' ')}
        </div>

        {result.requires_human_review && (
          <div className="mt-4 text-sm text-amber-700 bg-amber-50 px-4 py-2 rounded-lg inline-block">
            Human review recommended
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={onNext}
          className="bg-aqua-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-aqua-700 transition"
        >
          View Explanation →
        </button>
      </div>
    </div>
  )
}
