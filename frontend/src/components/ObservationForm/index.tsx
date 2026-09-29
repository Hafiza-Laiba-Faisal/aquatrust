import { useState } from 'react'

interface Props {
  onSubmit: (data: any) => void
  loading: boolean
}

export default function ObservationForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState({
    latitude: 52.123,
    longitude: 5.123,
    water_clarity: '',
    visible_waste: false,
    algae: false,
    odor: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      latitude: form.latitude,
      longitude: form.longitude,
      water_clarity: form.water_clarity || null,
      visible_waste: form.visible_waste,
      algae: form.algae,
      odor: form.odor || null,
    })
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">Citizen Observation</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Latitude</label>
            <input
              type="number"
              step="any"
              value={form.latitude}
              onChange={(e) => setForm({ ...form, latitude: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-aqua-500 focus:border-aqua-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Longitude</label>
            <input
              type="number"
              step="any"
              value={form.longitude}
              onChange={(e) => setForm({ ...form, longitude: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-aqua-500 focus:border-aqua-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Water Clarity</label>
          <select
            value={form.water_clarity}
            onChange={(e) => setForm({ ...form, water_clarity: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-aqua-500 focus:border-aqua-500"
          >
            <option value="">Select...</option>
            <option value="clear">Clear</option>
            <option value="slightly_cloudy">Slightly Cloudy</option>
            <option value="cloudy">Cloudy</option>
            <option value="opaque">Opaque</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="waste"
              checked={form.visible_waste}
              onChange={(e) => setForm({ ...form, visible_waste: e.target.checked })}
              className="w-4 h-4 text-aqua-600 rounded"
            />
            <label htmlFor="waste" className="text-sm text-slate-700">Visible Waste</label>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="algae"
              checked={form.algae}
              onChange={(e) => setForm({ ...form, algae: e.target.checked })}
              className="w-4 h-4 text-aqua-600 rounded"
            />
            <label htmlFor="algae" className="text-sm text-slate-700">Algae Present</label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Odor</label>
          <select
            value={form.odor}
            onChange={(e) => setForm({ ...form, odor: e.target.value })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-aqua-500 focus:border-aqua-500"
          >
            <option value="">Select...</option>
            <option value="none">None</option>
            <option value="earthy">Earthy</option>
            <option value="chemical">Chemical</option>
            <option value="sewage">Sewage</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-aqua-600 text-white py-2.5 rounded-lg font-medium hover:bg-aqua-700 transition disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit Observation'}
        </button>
      </form>
    </div>
  )
}
