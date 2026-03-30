import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fetchLeaderboard, fetchNodes, simulateFailure, simulateRecovery } from '../api'
import { Shield, Trophy, Zap, AlertTriangle } from 'lucide-react'

const BADGE_CONFIG = {
  Pioneer: { color: '#f59e0b', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', icon: '🏆' },
  Veteran: { color: '#00d4ff', bg: 'rgba(0,212,255,0.10)', border: 'rgba(0,212,255,0.25)', icon: '⭐' },
  Reliable: { color: '#10b981', bg: 'rgba(16,185,129,0.10)', border: 'rgba(16,185,129,0.25)', icon: '✅' },
  Newcomer: { color: '#94a3b8', bg: 'rgba(148,163,184,0.08)', border: 'rgba(148,163,184,0.2)', icon: '🆕' },
  Unstable: { color: '#ef4444', bg: 'rgba(239,68,68,0.10)', border: 'rgba(239,68,68,0.25)', icon: '⚠️' },
}

function TrustBar({ score }) {
  const color = score >= 85 ? '#f59e0b' : score >= 70 ? '#00d4ff' : score >= 50 ? '#10b981' : '#ef4444'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 rounded-full" style={{ background: '#1e1e30' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, ${color}, ${color}aa)`, boxShadow: `0 0 8px ${color}55` }}
        />
      </div>
      <span className="text-sm font-bold font-mono" style={{ color, minWidth: 36 }}>{score.toFixed(1)}</span>
    </div>
  )
}

export default function TrustLeaderboard() {
  const { data: leaderboard = [], refetch } = useQuery({ queryKey: ['leaderboard'], queryFn: fetchLeaderboard })
  const [event, setEvent] = useState(null)
  const [loading, setLoading] = useState(false)

  const chartData = leaderboard.map(n => ({ name: n.name, trust: n.trust_score }))

  const handleAction = async (nodeId, action) => {
    if (loading) return
    setLoading(true)
    try {
      const res = action === 'fail'
        ? await simulateFailure(nodeId)
        : await simulateRecovery(nodeId)
      setEvent(res.message || `Node action complete`)
      setTimeout(() => refetch(), 500)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 min-h-screen">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">Trust Leaderboard</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm mt-1">
          Dynamic trust scores updated after every job. Badge system rewards reliability & speed.
        </p>
      </motion.div>

      {event && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
          className="mb-4 px-4 py-2 rounded-xl text-sm"
          style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', color: '#00d4ff' }}>
          {event}
        </motion.div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {/* Leaderboard List */}
        <div className="col-span-2 space-y-3">
          {leaderboard.map((node, i) => {
            const badge = BADGE_CONFIG[node.badge] || BADGE_CONFIG.Newcomer
            return (
              <motion.div key={node.node_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.07 }}
                className="glass-card glass-card-hover p-5"
              >
                <div className="flex items-center gap-4 mb-4">
                  {/* Rank */}
                  <div className="w-8 text-center">
                    {i === 0 ? <span className="text-2xl">🥇</span> :
                     i === 1 ? <span className="text-2xl">🥈</span> :
                     i === 2 ? <span className="text-2xl">🥉</span> :
                     <span className="text-lg font-bold text-nebula-text-dim">#{node.rank}</span>}
                  </div>
                  {/* Name + Badge */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-nebula-text-primary">{node.name}</span>
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider"
                        style={{ background: badge.bg, border: `1px solid ${badge.border}`, color: badge.color }}>
                        {badge.icon} {node.badge}
                      </span>
                    </div>
                    <TrustBar score={node.trust_score} />
                  </div>
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-sm font-bold text-nebula-green">{node.jobs_completed}</div>
                      <div className="text-[10px] text-nebula-text-dim">Jobs</div>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-nebula-red">{node.failure_count}</div>
                      <div className="text-[10px] text-nebula-text-dim">Failures</div>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-nebula-cyan">{(node.reliability * 100).toFixed(0)}%</div>
                      <div className="text-[10px] text-nebula-text-dim">Reliability</div>
                    </div>
                  </div>
                  {/* Actions */}
                  <div className="flex gap-2">
                    <button onClick={() => handleAction(node.node_id, 'fail')}
                      disabled={loading}
                      className="px-2 py-1 rounded-lg text-[10px] font-medium transition-all"
                      style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', color: '#ef4444' }}>
                      Fail
                    </button>
                    <button onClick={() => handleAction(node.node_id, 'recover')}
                      disabled={loading}
                      className="px-2 py-1 rounded-lg text-[10px] font-medium transition-all"
                      style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', color: '#10b981' }}>
                      Recover
                    </button>
                  </div>
                </div>

                {/* History Sparkline */}
                {node.history?.length > 2 && (
                  <div className="mt-2 pt-3" style={{ borderTop: '1px solid #1e1e30' }}>
                    <div className="text-[10px] text-nebula-text-dim mb-1">Recent trust history</div>
                    <div className="flex items-end gap-1 h-6">
                      {node.history.slice(-10).map((h, j) => (
                        <div key={j} className="flex-1 rounded-sm transition-all"
                          style={{
                            height: `${(h.score / 100) * 24}px`,
                            background: h.success ? '#10b981' : '#ef4444',
                            opacity: 0.6 + (j / 10) * 0.4,
                          }} />
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Bar Chart */}
        <div className="space-y-4">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="glass-card p-5">
            <h3 className="text-sm font-semibold text-nebula-text-primary mb-4">Trust Score Comparison</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e30" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10, fill: '#475569' }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#94a3b8' }} width={50} />
                <Tooltip
                  contentStyle={{ background: '#13131f', border: '1px solid #1e1e30', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="trust" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, i) => {
                    const s = entry.trust
                    const c = s >= 85 ? '#f59e0b' : s >= 70 ? '#00d4ff' : s >= 50 ? '#10b981' : '#ef4444'
                    return <Cell key={i} fill={c} />
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Legend */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
            className="glass-card p-5">
            <h3 className="text-sm font-semibold text-nebula-text-primary mb-3">Badge System</h3>
            <div className="space-y-2">
              {Object.entries(BADGE_CONFIG).map(([name, cfg]) => (
                <div key={name} className="flex items-center gap-3">
                  <span className="text-sm">{cfg.icon}</span>
                  <span className="text-sm font-medium" style={{ color: cfg.color }}>{name}</span>
                  <span className="text-xs text-nebula-text-dim ml-auto">
                    {name === 'Pioneer' ? '≥85' : name === 'Veteran' ? '≥70' :
                     name === 'Reliable' ? '≥50' : name === 'Newcomer' ? '≥30' : '<30'}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
