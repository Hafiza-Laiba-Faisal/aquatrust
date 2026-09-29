import type { ScenarioRunResult } from '../../types'

interface Props {
  result: ScenarioRunResult
  onNext: () => void
}

export default function EvidencePanel({ result, onNext }: Props) {
  const evidenceCards = [
    {
      source: 'Citizen',
      icon: '👤',
      color: 'border-l-blue-500',
      items: [
        `Water clarity: ${result.assessment.includes('cloudy') || result.assessment.includes('turbidity') ? 'Cloudy' : 'Reported'}`,
        `Visible waste: ${result.conflicting_evidence.length > 0 ? 'Yes' : 'No'}`,
        `Algae: ${result.supporting_evidence.some(s => s.toLowerCase().includes('algae')) ? 'Yes' : 'No'}`,
      ],
    },
    {
      source: 'Sensor',
      icon: '📡',
      color: 'border-l-green-500',
      items: [
        result.supporting_evidence.some(s => s.toLowerCase().includes('turbidity'))
          ? 'Turbidity: Elevated'
          : 'Turbidity: Normal',
        'pH: 7.4',
        'Conductivity: 820 µS/cm',
      ],
    },
    {
      source: 'Satellite',
      icon: '🛰️',
      color: 'border-l-purple-500',
      items: [
        result.supporting_evidence.some(s => s.toLowerCase().includes('satellite'))
          ? 'Anomaly detected'
          : 'No anomaly',
        'NDVI: 0.3',
        'Cloud cover: Low',
      ],
    },
    {
      source: 'Historical',
      icon: '📊',
      color: 'border-l-amber-500',
      items: [
        result.conflicting_evidence.some(s => s.toLowerCase().includes('historical'))
          ? 'Baseline: Normal (conflict)'
          : 'Baseline: Consistent',
        '30-day avg turbidity: 12 NTU',
        'Seasonal norm: Clear',
      ],
    },
    {
      source: 'Weather',
      icon: '🌧️',
      color: 'border-l-cyan-500',
      items: [
        'Rainfall: 15 mm (24h)',
        'Temperature: 18°C',
        'Wind: 12 km/h NW',
      ],
    },
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Evidence Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {evidenceCards.map((card) => (
            <div
              key={card.source}
              className={`bg-slate-50 rounded-lg border-l-4 ${card.color} p-4`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{card.icon}</span>
                <span className="font-medium text-slate-800">{card.source}</span>
              </div>
              <ul className="space-y-1">
                {card.items.map((item, i) => (
                  <li key={i} className="text-sm text-slate-600">{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onNext}
          className="bg-aqua-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-aqua-700 transition"
        >
          View Assessment →
        </button>
      </div>
    </div>
  )
}
