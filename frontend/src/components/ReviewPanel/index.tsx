import { useState } from 'react'
import { api } from '../../api/client'

interface Props {
  assessmentId: string
}

export default function ReviewPanel({ assessmentId }: Props) {
  const [decision, setDecision] = useState<string>('')
  const [comment, setComment] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!decision) return

    setLoading(true)
    setError(null)
    try {
      await api.createReview({
        assessment_id: assessmentId,
        reviewer_decision: decision,
        reviewer_comment: comment || undefined,
      })
      setSubmitted(true)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
        <div className="text-green-600 text-lg font-medium mb-2">Human review recorded</div>
        <p className="text-sm text-green-700">
          The review decision has been stored as a separate provenance event.
          The original AI/system assessment is preserved.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">Human Review</h2>
      <p className="text-sm text-slate-500 mb-4">
        A reviewer can approve, reject, or modify the assessment. The original AI assessment is always preserved.
      </p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Decision</label>
          <div className="flex gap-3">
            {['confirmed', 'rejected', 'needs_more_evidence'].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDecision(d)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition ${
                  decision === d
                    ? 'bg-aqua-600 text-white border-aqua-600'
                    : 'bg-white text-slate-700 border-slate-300 hover:border-aqua-400'
                }`}
              >
                {d.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Comment (optional)</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-aqua-500 focus:border-aqua-500 text-sm"
            placeholder="Add a review comment..."
          />
        </div>

        <button
          type="submit"
          disabled={!decision || loading}
          className="bg-aqua-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-aqua-700 transition disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  )
}
