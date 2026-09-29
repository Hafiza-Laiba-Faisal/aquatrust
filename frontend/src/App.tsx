import { useState } from 'react'
import { api } from './api/client'
import type { Scenario, ScenarioRunResult } from './types'
import ObservationForm from './components/ObservationForm'
import EvidencePanel from './components/EvidencePanel'
import ConfidenceCard from './components/ConfidenceCard'
import ConflictPanel from './components/ConflictPanel'
import ReviewPanel from './components/ReviewPanel'
import NextEvidenceCard from './components/NextEvidenceCard'

type Step = 'observation' | 'evidence' | 'assessment' | 'explanation' | 'action'

export default function App() {
  const [step, setStep] = useState<Step>('observation')
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null)
  const [result, setResult] = useState<ScenarioRunResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadScenarios = async () => {
    try {
      const data = await api.getScenarios()
      setScenarios(data.scenarios)
    } catch (e: any) {
      setError(e.message)
    }
  }

  const runScenario = async (scenarioId: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.runScenario(scenarioId)
      setResult(res)
      setStep('evidence')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const submitObservation = async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      await api.createObservation(data)
      setStep('evidence')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStep('observation')
    setResult(null)
    setSelectedScenario(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-aqua-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-aqua-800">AquaTrust</h1>
            <p className="text-sm text-slate-500">Evidence-Aware AI for Reliable Citizen Freshwater Observations</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full font-medium">
              Research Prototype
            </span>
            {result && (
              <button
                onClick={reset}
                className="text-sm text-aqua-600 hover:text-aqua-800 font-medium"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {(['observation', 'evidence', 'assessment', 'explanation', 'action'] as Step[]).map((s, i) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === s
                    ? 'bg-aqua-600 text-white'
                    : 'bg-slate-200 text-slate-500'
                }`}
              >
                {i + 1}
              </div>
              {i < 4 && <div className="w-8 h-0.5 bg-slate-200 mx-1" />}
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Step 1: Observation */}
        {step === 'observation' && (
          <div className="space-y-6">
            <ObservationForm onSubmit={submitObservation} loading={loading} />

            {/* Demo Scenarios */}
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-2">Demo Scenarios</h2>
              <p className="text-sm text-slate-500 mb-4">
                Select a scenario to quickly reproduce the four deterministic demo cases.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {scenarios.length === 0 ? (
                  <button
                    onClick={loadScenarios}
                    className="col-span-full text-sm text-aqua-600 hover:text-aqua-800 font-medium"
                  >
                    Load Scenarios
                  </button>
                ) : (
                  scenarios.map((s) => (
                    <button
                      key={s.scenario_id}
                      onClick={() => runScenario(s.scenario_id)}
                      disabled={loading}
                      className={`text-left p-4 rounded-lg border transition ${
                        selectedScenario === s.scenario_id
                          ? 'border-aqua-500 bg-aqua-50'
                          : 'border-slate-200 hover:border-aqua-300 hover:bg-aqua-50/50'
                      }`}
                    >
                      <div className="font-medium text-slate-800">{s.name}</div>
                      <div className="text-xs text-slate-500 mt-1">{s.description}</div>
                      <div className="text-xs text-aqua-600 mt-2">
                        Expected: <span className="font-medium">{s.expected_status}</span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <>
            {step === 'evidence' && (
              <EvidencePanel result={result} onNext={() => setStep('assessment')} />
            )}
            {step === 'assessment' && (
              <ConfidenceCard result={result} onNext={() => setStep('explanation')} />
            )}
            {step === 'explanation' && (
              <ConflictPanel result={result} onNext={() => setStep('action')} />
            )}
            {step === 'action' && (
              <div className="space-y-6">
                <NextEvidenceCard result={result} />
                <ReviewPanel assessmentId={result.assessment_id} />
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white/50 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-sm text-slate-400">
          AquaTrust — Research prototype for OneAquaHealth IEEE Global Hackathon 2026, Track 3: AI-Supported Assessment.
          Not a certified environmental or health diagnosis.
        </div>
      </footer>
    </div>
  )
}
