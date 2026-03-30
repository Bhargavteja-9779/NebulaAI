import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, AreaChart, Area, BarChart, Bar
} from 'recharts'
import { fetchJobs, fetchDigitalTwin } from '../api'
import { Activity, Cpu, Target, Clock } from 'lucide-react'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-3 py-2" style={{ border: '1px solid #1e1e30' }}>
      <div className="text-xs text-nebula-text-dim mb-1">Epoch {label}</div>
      {payload.map(p => (
        <div key={p.name} className="text-xs font-mono" style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(3) : p.value}
        </div>
      ))}
    </div>
  )
}

export default function TrainingMonitor() {
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs })
  const [selectedId, setSelectedId] = useState(null)
  const [showTwin, setShowTwin] = useState(false)
  const { data: twin } = useQuery({
    queryKey: ['twin', selectedId],
    queryFn: () => fetchDigitalTwin(selectedId),
    enabled: !!selectedId && showTwin,
  })

  const activeJobs = jobs.filter(j => j.status === 'running' || j.status === 'completed')
  const selectedJob = jobs.find(j => j.id === selectedId) || activeJobs[0]

  const chartData = selectedJob?.loss_history?.map((loss, i) => ({
    epoch: i + 1,
    loss,
    accuracy: selectedJob.accuracy_history?.[i],
  })) || []

  const twinData = twin ? twin.real_loss_curve?.map((rl, i) => ({
    epoch: i + 1,
    'Real Loss': rl,
    'Predicted Loss': twin.predicted_loss_curve?.[i],
  })) : []

  return (
    <div className="p-8 min-h-screen">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">Training Monitor</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm mt-1">
          Live loss/accuracy curves, compute usage, and digital twin comparison.
        </p>
      </motion.div>

      {/* Job Selector */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {activeJobs.map(j => (
          <button key={j.id}
            onClick={() => { setSelectedId(j.id); setShowTwin(false) }}
            className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
            style={{
              background: selectedId === j.id || (!selectedId && j === selectedJob)
                ? 'rgba(0,212,255,0.15)' : 'rgba(255,255,255,0.03)',
              border: selectedId === j.id || (!selectedId && j === selectedJob)
                ? '1px solid rgba(0,212,255,0.3)' : '1px solid #1e1e30',
              color: selectedId === j.id || (!selectedId && j === selectedJob)
                ? '#00d4ff' : '#94a3b8',
            }}>
            {j.name}
          </button>
        ))}
      </div>

      {selectedJob ? (
        <>
          {/* Stats Row */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { icon: Activity, label: 'Progress', value: `${selectedJob.progress?.toFixed(0)}%`, color: '#00d4ff' },
              { icon: Target, label: 'Accuracy', value: `${(selectedJob.current_accuracy || 0).toFixed(1)}%`, color: '#10b981' },
              { icon: Cpu, label: 'Loss', value: (selectedJob.current_loss || 0).toFixed(4), color: '#7c3aed' },
              { icon: Clock, label: 'Est. Time', value: `${Math.round(selectedJob.estimated_time)}s`, color: '#f59e0b' },
            ].map(({ icon: Icon, label, value, color }, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.07 }}
                className="glass-card p-5 text-center">
                <Icon size={18} style={{ color, margin: '0 auto 8px' }} />
                <div className="text-2xl font-bold font-mono" style={{ color }}>{value}</div>
                <div className="text-xs text-nebula-text-dim mt-1">{label}</div>
              </motion.div>
            ))}
          </div>

          {/* Progress Bar */}
          <div className="glass-card p-5 mb-6">
            <div className="flex justify-between text-xs mb-2">
              <span className="text-nebula-text-secondary">Training Progress</span>
              <span className="text-nebula-cyan font-mono">{selectedJob.progress?.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${selectedJob.progress}%` }}
                transition={{ duration: 1.2, ease: 'easeOut' }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-nebula-text-dim mt-2">
              <span>Nodes: {selectedJob.allocated_nodes?.join(', ')}</span>
              <span>{selectedJob.model_type} · {selectedJob.dataset}</span>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
              className="glass-card p-6">
              <h3 className="text-sm font-semibold text-nebula-text-primary mb-4">Training Loss</h3>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="lossGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                  <XAxis dataKey="epoch" tick={{ fontSize: 10, fill: '#475569' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#475569' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="loss" stroke="#7c3aed" fill="url(#lossGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
              className="glass-card p-6">
              <h3 className="text-sm font-semibold text-nebula-text-primary mb-4">Accuracy</h3>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="accGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                  <XAxis dataKey="epoch" tick={{ fontSize: 10, fill: '#475569' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#475569' }} domain={[0, 100]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="accuracy" stroke="#10b981" fill="url(#accGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          {/* Digital Twin */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-nebula-text-primary">🤖 Digital Twin Comparison</h3>
              <button
                onClick={() => setShowTwin(true)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)', color: '#00d4ff' }}>
                {showTwin ? 'Refreshing...' : 'Generate Twin'}
              </button>
            </div>
            {twin ? (
              <>
                <div className="flex gap-4 mb-4">
                  <div className="glass-card px-4 py-2 text-center">
                    <div className="text-lg font-bold text-nebula-cyan font-mono">{twin.twin_accuracy}%</div>
                    <div className="text-xs text-nebula-text-dim">Twin Accuracy</div>
                  </div>
                  <div className="glass-card px-4 py-2 text-center">
                    <div className="text-lg font-bold text-nebula-yellow font-mono">{twin.variance_percent}%</div>
                    <div className="text-xs text-nebula-text-dim">Variance</div>
                  </div>
                  <div className="glass-card px-4 py-2 text-center">
                    <div className="text-lg font-bold text-nebula-green font-mono">{twin.actual_time_seconds}s</div>
                    <div className="text-xs text-nebula-text-dim">Actual Time</div>
                  </div>
                  <div className="glass-card px-4 py-2 text-center">
                    <div className="text-lg font-bold text-purple-400 font-mono">{twin.predicted_time_seconds}s</div>
                    <div className="text-xs text-nebula-text-dim">Predicted Time</div>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={twinData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                    <XAxis dataKey="epoch" tick={{ fontSize: 10, fill: '#475569' }} />
                    <YAxis tick={{ fontSize: 10, fill: '#475569' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                    <Line type="monotone" dataKey="Real Loss" stroke="#00d4ff" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Predicted Loss" stroke="#7c3aed" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </>
            ) : (
              <div className="text-center py-8 text-nebula-text-dim text-sm">
                Click "Generate Twin" to compare real vs predicted training curves
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="glass-card p-12 text-center">
          <Activity size={40} className="mx-auto mb-3 text-nebula-text-dim" />
          <div className="text-nebula-text-secondary">No jobs yet. Submit one via the AI Orchestrator.</div>
        </div>
      )}
    </div>
  )
}
