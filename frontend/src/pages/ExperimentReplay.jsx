import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchExperiments } from '../api'
import { Play, Pause, SkipBack, ChevronRight } from 'lucide-react'

export default function ExperimentReplay() {
  const { data: experiments = [] } = useQuery({ queryKey: ['experiments'], queryFn: fetchExperiments })
  const [selectedExp, setSelectedExp] = useState(null)
  const [timelineIdx, setTimelineIdx] = useState(0)
  const [playing, setPlaying] = useState(false)

  const exp = selectedExp ? experiments.find(e => e.id === selectedExp) : experiments[0]

  const events = exp?.timeline_events || []
  const currentEvent = events[timelineIdx]

  const chartData = exp?.result_snapshot?.final_accuracy
    ? Array.from({ length: exp.config?.epochs || 10 }, (_, i) => {
        const prog = i / ((exp.config?.epochs || 10) - 1)
        return {
          epoch: i + 1,
          loss: Math.max(0.05, 2.3 * Math.pow(1 - prog, 1.8) + 0.05),
          accuracy: 10 + (exp.result_snapshot.final_accuracy - 10) * (1 - Math.pow(1 - prog, 2)),
        }
      })
    : []

  const handlePlay = () => {
    if (playing) { setPlaying(false); return }
    setPlaying(true)
    let idx = timelineIdx
    const interval = setInterval(() => {
      idx++
      if (idx >= events.length) { clearInterval(interval); setPlaying(false) }
      else setTimelineIdx(idx)
    }, 1200)
  }

  return (
    <div className="p-8 min-h-screen">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">Experiment Replay</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm mt-1">
          Step through past training experiments. Replay the timeline event-by-event.
        </p>
      </motion.div>

      <div className="grid grid-cols-4 gap-6">
        {/* Experiment List */}
        <div className="col-span-1 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-widest text-nebula-text-dim mb-3">Experiments</div>
          {experiments.map(e => (
            <button key={e.id}
              onClick={() => { setSelectedExp(e.id); setTimelineIdx(0); setPlaying(false) }}
              className="w-full text-left px-4 py-3 rounded-xl transition-all"
              style={{
                background: (selectedExp === e.id || (!selectedExp && e === experiments[0]))
                  ? 'rgba(0,212,255,0.08)' : 'rgba(255,255,255,0.02)',
                border: (selectedExp === e.id || (!selectedExp && e === experiments[0]))
                  ? '1px solid rgba(0,212,255,0.2)' : '1px solid #1e1e30',
              }}>
              <div className="text-sm font-medium text-nebula-text-primary">{e.name}</div>
              <div className="text-xs text-nebula-text-dim mt-1">{e.config?.model} · {e.config?.dataset}</div>
              <div className="flex gap-1 mt-2 flex-wrap">
                {(e.tags || []).map(t => (
                  <span key={t} className="px-1.5 py-0.5 rounded text-[9px] font-medium"
                    style={{ background: 'rgba(124,58,237,0.15)', color: '#a78bfa' }}>
                    {t}
                  </span>
                ))}
              </div>
            </button>
          ))}
          {!experiments.length && (
            <div className="text-nebula-text-dim text-sm text-center py-4">No experiments yet</div>
          )}
        </div>

        {/* Replay Area */}
        {exp ? (
          <div className="col-span-3 space-y-5">
            {/* Config */}
            <div className="glass-card p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-nebula-text-primary">{exp.name}</h3>
                <div className="flex gap-2">
                  {exp.result_snapshot?.final_accuracy && (
                    <span className="px-3 py-1 rounded-lg text-xs font-bold"
                      style={{ background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.3)' }}>
                      🎯 {exp.result_snapshot.final_accuracy}% Accuracy
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-4 text-xs">
                {Object.entries(exp.config || {}).map(([k, v]) => (
                  <div key={k}>
                    <span className="text-nebula-text-dim">{k}: </span>
                    <span className="text-nebula-cyan font-mono">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Timeline Player */}
            <div className="glass-card p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-nebula-text-primary">Timeline Replay</h3>
                <div className="flex items-center gap-2">
                  <button onClick={() => { setTimelineIdx(0); setPlaying(false) }}
                    className="p-2 rounded-lg transition-all hover:bg-white/5">
                    <SkipBack size={14} className="text-nebula-text-secondary" />
                  </button>
                  <button onClick={handlePlay}
                    className="px-3 py-1.5 rounded-lg flex items-center gap-1.5 text-xs font-medium"
                    style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)', color: '#00d4ff' }}>
                    {playing ? <Pause size={12} /> : <Play size={12} />}
                    {playing ? 'Pause' : 'Play'}
                  </button>
                </div>
              </div>

              {/* Timeline Track */}
              <div className="relative mb-5">
                <div className="h-1 rounded-full" style={{ background: '#1e1e30' }}>
                  <motion.div className="h-full rounded-full"
                    style={{ background: 'linear-gradient(90deg,#00d4ff,#7c3aed)' }}
                    animate={{ width: `${events.length > 1 ? (timelineIdx / (events.length - 1)) * 100 : 0}%` }}
                    transition={{ duration: 0.4 }}
                  />
                </div>
                <div className="flex justify-between mt-2">
                  {events.map((e, i) => (
                    <button key={i} onClick={() => setTimelineIdx(i)}
                      className="flex flex-col items-center gap-1 cursor-pointer"
                      style={{ flex: 1 }}>
                      <div className="w-2.5 h-2.5 rounded-full border-2 transition-all"
                        style={{
                          borderColor: i <= timelineIdx ? '#00d4ff' : '#1e1e30',
                          background: i <= timelineIdx ? '#00d4ff' : '#0e0e1a',
                          boxShadow: i === timelineIdx ? '0 0 8px #00d4ff' : 'none',
                        }} />
                    </button>
                  ))}
                </div>
              </div>

              {/* Current Event */}
              <AnimatePresence mode="wait">
                {currentEvent && (
                  <motion.div key={timelineIdx}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="rounded-xl px-4 py-3"
                    style={{ background: 'rgba(0,212,255,0.05)', border: '1px solid rgba(0,212,255,0.15)' }}>
                    <div className="flex items-center gap-2 mb-1">
                      <ChevronRight size={12} className="text-nebula-cyan" />
                      <span className="text-sm font-medium text-nebula-text-primary">{currentEvent.event}</span>
                      <span className="ml-auto text-xs font-mono text-nebula-text-dim">t={currentEvent.t}s</span>
                    </div>
                    {currentEvent.note && (
                      <div className="text-xs text-nebula-text-secondary ml-4">{currentEvent.note}</div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Event Log */}
              <div className="mt-4 space-y-1 max-h-32 overflow-y-auto">
                {events.map((e, i) => (
                  <div key={i}
                    className="flex items-center gap-3 py-1 px-2 rounded-lg text-xs cursor-pointer transition-all"
                    style={{ background: i === timelineIdx ? 'rgba(0,212,255,0.06)' : 'transparent',
                             opacity: i <= timelineIdx ? 1 : 0.3 }}
                    onClick={() => setTimelineIdx(i)}>
                    <span className="font-mono text-nebula-text-dim w-12">t={e.t}s</span>
                    <span className="text-nebula-text-secondary">{e.event}</span>
                    {e.note && <span className="text-nebula-cyan ml-auto">{e.note}</span>}
                  </div>
                ))}
              </div>
            </div>

            {/* Charts */}
            {chartData.length > 0 && (
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-nebula-text-primary mb-4">Training Curves</h3>
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" />
                    <XAxis dataKey="epoch" tick={{ fontSize: 10, fill: '#475569' }} />
                    <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#475569' }} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#475569' }} domain={[0, 100]} />
                    <Tooltip contentStyle={{ background: '#13131f', border: '1px solid #1e1e30', borderRadius: '8px', fontSize: '11px' }} />
                    <Line yAxisId="left" type="monotone" dataKey="loss" stroke="#7c3aed" strokeWidth={2} dot={false} name="Loss" />
                    <Line yAxisId="right" type="monotone" dataKey="accuracy" stroke="#10b981" strokeWidth={2} dot={false} name="Accuracy %" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        ) : (
          <div className="col-span-3 glass-card flex items-center justify-center" style={{ minHeight: 300 }}>
            <div className="text-nebula-text-dim text-sm">Select an experiment to replay</div>
          </div>
        )}
      </div>
    </div>
  )
}
