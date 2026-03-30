import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useEffect, useState, useRef } from 'react'
import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts'
import { Cpu, Activity, CheckCircle, Zap, TrendingUp, Clock, Server, AlertTriangle } from 'lucide-react'
import { fetchNodes, fetchJobs } from '../api'

const TICKER_MESSAGES = [
  '🟢 Atlas: Training ResNet-50 epoch 7/20',
  '⚡ Scheduler: Allocated 3 nodes for MNIST job',
  '✅ Verifier: Job feasibility confirmed',
  '🔄 Optimizer: Tuned LR from 0.001 → 0.01',
  '📡 Orion: Heartbeat received',
  '🧠 Planner: Decomposed user intent into 4 sub-tasks',
  '⚠️ Quasar: High load detected',
  '✅ Job #3 completed: 97.8% accuracy',
]

function StatCard({ icon: Icon, label, value, sub, color = 'cyan', delay = 0 }) {
  const colorMap = {
    cyan: { text: 'text-nebula-cyan', bg: 'bg-nebula-cyan/10', border: 'border-nebula-cyan/20' },
    purple: { text: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
    green: { text: 'text-nebula-green', bg: 'bg-nebula-green/10', border: 'border-nebula-green/20' },
    yellow: { text: 'text-nebula-yellow', bg: 'bg-nebula-yellow/10', border: 'border-nebula-yellow/20' },
  }
  const c = colorMap[color]
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`glass-card glass-card-hover p-6 border ${c.border}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2.5 rounded-xl ${c.bg}`}>
          <Icon size={20} className={c.text} />
        </div>
      </div>
      <div className={`text-3xl font-bold ${c.text} mb-1`}>{value}</div>
      <div className="text-nebula-text-secondary text-sm font-medium">{label}</div>
      {sub && <div className="text-nebula-text-dim text-xs mt-1">{sub}</div>}
    </motion.div>
  )
}

function LiveTicker() {
  const [idx, setIdx] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setIdx(i => (i + 1) % TICKER_MESSAGES.length), 2500)
    return () => clearInterval(t)
  }, [])
  return (
    <div className="px-4 py-2 rounded-xl text-xs font-mono text-nebula-text-secondary"
      style={{ background: 'rgba(0,212,255,0.04)', border: '1px solid rgba(0,212,255,0.1)' }}>
      <motion.span
        key={idx}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {TICKER_MESSAGES[idx]}
      </motion.span>
    </div>
  )
}

export default function Dashboard() {
  const { data: nodes = [] } = useQuery({ queryKey: ['nodes'], queryFn: fetchNodes })
  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: fetchJobs })

  const onlineNodes = nodes.filter(n => n.status === 'online').length
  const runningJobs = jobs.filter(j => j.status === 'running').length
  const completedJobs = jobs.filter(j => j.status === 'completed').length
  const avgAccuracy = completedJobs > 0
    ? (jobs.filter(j => j.final_accuracy).reduce((a, j) => a + j.final_accuracy, 0) / completedJobs).toFixed(1)
    : '—'

  const [metrics, setMetrics] = useState(Array(20).fill(0).map((_, i) => ({ t: i, v: 40 + Math.random() * 30 })))
  useEffect(() => {
    const t = setInterval(() => {
      setMetrics(m => [...m.slice(1), { t: m[m.length - 1].t + 1, v: 35 + Math.random() * 50 }])
    }, 1500)
    return () => clearInterval(t)
  }, [])

  const recentJobs = jobs.slice(0, 6)

  return (
    <div className="p-8 min-h-screen">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold">
              <span className="gradient-text">NebulaAI</span>{' '}
              <span className="text-nebula-text-primary">Control Center</span>
            </h1>
            <p className="text-nebula-text-secondary mt-1 text-sm">
              Transforming idle devices into a self-organizing AI supercomputer
            </p>
          </div>
          <div className="flex items-center gap-3">
            <LiveTicker />
            <div className="px-3 py-1.5 rounded-lg text-xs font-medium"
              style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', color: '#10b981' }}>
              ● All Systems Go
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-5 mb-8">
        <StatCard icon={Server} label="Active Nodes" value={onlineNodes} sub={`${nodes.length} registered`} color="cyan" delay={0} />
        <StatCard icon={Cpu} label="Running Jobs" value={runningJobs} sub="Training in progress" color="purple" delay={0.08} />
        <StatCard icon={CheckCircle} label="Completed" value={completedJobs} sub="Total job runs" color="green" delay={0.16} />
        <StatCard icon={TrendingUp} label="Avg Accuracy" value={`${avgAccuracy}%`} sub="Across all models" color="yellow" delay={0.24} />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        {/* Compute Utilization */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6 col-span-2"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-nebula-text-primary">Compute Utilization (Live)</h2>
            <div className="flex items-center gap-2 text-xs text-nebula-text-dim">
              <span className="status-dot online" /> Real-time
            </div>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={metrics}>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#7c3aed" />
                </linearGradient>
              </defs>
              <Tooltip
                contentStyle={{ background: '#13131f', border: '1px solid #1e1e30', borderRadius: '8px', fontSize: '11px' }}
                formatter={(v) => [`${v.toFixed(1)}%`, 'Utilization']}
              />
              <Line type="monotone" dataKey="v" stroke="url(#grad)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Node Status */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="glass-card p-6"
        >
          <h2 className="font-semibold text-nebula-text-primary mb-4">Node Status</h2>
          <div className="space-y-3">
            {nodes.slice(0, 5).map((node) => (
              <div key={node.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`status-dot ${node.status}`} />
                  <span className="text-sm text-nebula-text-primary">{node.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-xs text-nebula-cyan font-mono">{node.trust_score.toFixed(1)}</div>
                  <div className="text-[10px] text-nebula-text-dim">trust</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Recent Jobs */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6"
      >
        <h2 className="font-semibold text-nebula-text-primary mb-4">Recent Jobs</h2>
        <div className="space-y-3">
          {recentJobs.map((job, i) => (
            <div key={job.id} className="flex items-center gap-4 p-3 rounded-xl"
              style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #1e1e30' }}>
              <div className={`px-2 py-0.5 rounded-md text-xs font-medium ${
                job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                job.status === 'running' ? 'bg-cyan-500/20 text-cyan-400' :
                'bg-yellow-500/20 text-yellow-400'
              }`}>{job.status}</div>
              <div className="flex-1">
                <div className="text-sm text-nebula-text-primary font-medium">{job.name}</div>
                <div className="text-xs text-nebula-text-dim">{job.model_type} · {job.dataset}</div>
              </div>
              <div className="flex items-center gap-4 text-right">
                <div>
                  <div className="text-xs text-nebula-cyan font-mono">{job.progress.toFixed(0)}%</div>
                  <div className="text-[10px] text-nebula-text-dim">progress</div>
                </div>
                {job.final_accuracy && (
                  <div>
                    <div className="text-xs text-nebula-green font-mono">{job.final_accuracy}%</div>
                    <div className="text-[10px] text-nebula-text-dim">accuracy</div>
                  </div>
                )}
                <div className="text-xs text-nebula-text-dim">
                  {job.allocated_nodes?.join(', ')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
