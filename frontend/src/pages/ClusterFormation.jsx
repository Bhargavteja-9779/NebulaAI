import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { fetchNodes } from '../api'
import { Zap, GitBranch } from 'lucide-react'

const CLUSTER_PHASES = [
  { id: 0, label: 'Discovery', desc: 'Nodes broadcasting presence via mDNS', color: '#475569' },
  { id: 1, label: 'Handshake', desc: 'Exchanging capability manifests', color: '#7c3aed' },
  { id: 2, label: 'Trust Verification', desc: 'Verifying node trust scores', color: '#f59e0b' },
  { id: 3, label: 'Cluster Formation', desc: 'Elected governor, forming topology', color: '#00d4ff' },
  { id: 4, label: 'Ready', desc: 'Cluster online — accepting workloads', color: '#10b981' },
]

const NODE_CIRCLE_POSITIONS = [
  { cx: 300, cy: 160 },
  { cx: 120, cy: 260 },
  { cx: 480, cy: 260 },
  { cx: 170, cy: 400 },
  { cx: 430, cy: 400 },
]

export default function ClusterFormation() {
  const { data: nodes = [] } = useQuery({ queryKey: ['nodes'], queryFn: fetchNodes })
  const [phase, setPhase] = useState(0)
  const [running, setRunning] = useState(false)
  const [edges, setEdges] = useState([])

  const runAnimation = async () => {
    if (running) return
    setRunning(true)
    setEdges([])
    setPhase(0)

    for (let p = 0; p <= 4; p++) {
      await new Promise(r => setTimeout(r, p === 0 ? 500 : 1200))
      setPhase(p)
      if (p >= 3) {
        const newEdges = []
        for (let i = 0; i < 5; i++) {
          for (let j = i + 1; j < 5; j++) {
            if (Math.random() > 0.25) newEdges.push([i, j])
          }
        }
        setEdges(newEdges)
      }
    }
    setRunning(false)
  }

  const phaseInfo = CLUSTER_PHASES[phase]

  return (
    <div className="p-8 min-h-screen">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">Cluster Formation</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm mt-1">
          Watch nodes discover, handshake, and self-organize into an AI compute cluster.
        </p>
      </motion.div>

      <div className="grid grid-cols-3 gap-6">
        {/* SVG Visualization */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="glass-card col-span-2 relative overflow-hidden">
          <div className="absolute inset-0"
            style={{ background: 'radial-gradient(ellipse at center, rgba(0,212,255,0.04) 0%, transparent 70%)' }} />

          <svg viewBox="0 0 600 520" className="w-full h-auto relative z-10">
            <defs>
              <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00d4ff" />
                <stop offset="100%" stopColor="#7c3aed" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>

            {/* Edges */}
            <AnimatePresence>
              {edges.map(([i, j], k) => {
                const a = NODE_CIRCLE_POSITIONS[i], b = NODE_CIRCLE_POSITIONS[j]
                return (
                  <motion.line key={k}
                    x1={a.cx} y1={a.cy} x2={b.cx} y2={b.cy}
                    stroke="#00d4ff" strokeWidth={1.5} strokeOpacity={0.4}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 0.5 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.6, delay: k * 0.08 }}
                    strokeDasharray="4 4"
                  />
                )
              })}
            </AnimatePresence>

            {/* Animated data packets */}
            {phase >= 3 && edges.slice(0, 4).map(([i, j], k) => {
              const a = NODE_CIRCLE_POSITIONS[i], b = NODE_CIRCLE_POSITIONS[j]
              return (
                <motion.circle key={`p-${k}`} r={3} fill="#00d4ff"
                  animate={{
                    cx: [a.cx, b.cx, a.cx],
                    cy: [a.cy, b.cy, a.cy],
                  }}
                  transition={{ duration: 2.5, delay: k * 0.5, repeat: Infinity, ease: 'linear' }}
                  filter="url(#glow)"
                />
              )
            })}

            {/* Nodes */}
            {NODE_CIRCLE_POSITIONS.map((pos, i) => {
              const node = nodes[i]
              const isActive = phase >= 1
              const color = phase >= 4 ? '#10b981' : phase >= 3 ? '#00d4ff' : phase >= 2 ? '#f59e0b' : '#7c3aed'
              return (
                <g key={i}>
                  {/* Glow ring */}
                  {isActive && (
                    <motion.circle cx={pos.cx} cy={pos.cy} r={36}
                      fill="none" stroke={color} strokeWidth={1} strokeOpacity={0.3}
                      animate={{ r: [34, 42, 34], strokeOpacity: [0.3, 0.1, 0.3] }}
                      transition={{ duration: 2, delay: i * 0.3, repeat: Infinity }}
                    />
                  )}
                  {/* Node circle */}
                  <motion.circle cx={pos.cx} cy={pos.cy} r={28}
                    fill="#0e0e1a"
                    stroke={isActive ? color : '#1e1e30'}
                    strokeWidth={2}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: i * 0.1, type: 'spring', stiffness: 200 }}
                    filter={isActive ? 'url(#glow)' : undefined}
                  />
                  {/* Icon */}
                  <text x={pos.cx} y={pos.cy - 4} textAnchor="middle" fontSize={14} dominantBaseline="middle">
                    {node?.node_type === 'gpu' ? '🖥️' : '💻'}
                  </text>
                  {/* Name */}
                  <text x={pos.cx} y={pos.cy + 14} textAnchor="middle" fontSize={9}
                    fill={isActive ? color : '#475569'} fontWeight="bold" fontFamily="Inter">
                    {node?.name || `Node ${i + 1}`}
                  </text>
                  {/* Trust score */}
                  {node && phase >= 2 && (
                    <motion.text x={pos.cx} y={pos.cy + 44} textAnchor="middle" fontSize={8}
                      fill="#94a3b8" fontFamily="JetBrains Mono"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}>
                      {node.trust_score?.toFixed(1)}
                    </motion.text>
                  )}
                </g>
              )
            })}

            {/* Governor crown */}
            {phase >= 3 && nodes[0] && (
              <motion.text x={NODE_CIRCLE_POSITIONS[0].cx} y={NODE_CIRCLE_POSITIONS[0].cy - 42}
                textAnchor="middle" fontSize={16}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}>
                👑
              </motion.text>
            )}
          </svg>
        </motion.div>

        {/* Phase Panel */}
        <div className="space-y-4">
          <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }}
            className="glass-card p-5">
            <h3 className="text-sm font-semibold text-nebula-text-primary mb-4">Formation Phases</h3>
            <div className="space-y-2">
              {CLUSTER_PHASES.map((p) => (
                <div key={p.id} className="flex items-start gap-3">
                  <div className="mt-0.5 w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-[10px] font-bold"
                    style={{
                      background: p.id <= phase ? p.color : '#1e1e30',
                      color: p.id <= phase ? '#000' : '#475569',
                    }}>
                    {p.id < phase ? '✓' : p.id + 1}
                  </div>
                  <div>
                    <div className="text-xs font-semibold" style={{ color: p.id <= phase ? p.color : '#475569' }}>
                      {p.label}
                    </div>
                    <div className="text-[10px] text-nebula-text-dim">{p.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Current Phase Banner */}
          <AnimatePresence mode="wait">
            <motion.div key={phase}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass-card p-4"
              style={{ borderColor: `${phaseInfo.color}40` }}>
              <div className="text-xs font-semibold mb-1" style={{ color: phaseInfo.color }}>
                Phase {phase + 1}: {phaseInfo.label}
              </div>
              <div className="text-xs text-nebula-text-secondary">{phaseInfo.desc}</div>
            </motion.div>
          </AnimatePresence>

          {/* Launch Button */}
          <button onClick={runAnimation} disabled={running}
            className="w-full py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-all"
            style={{
              background: running ? 'rgba(255,255,255,0.03)' : 'linear-gradient(135deg,#00d4ff,#7c3aed)',
              color: running ? '#475569' : '#fff',
              cursor: running ? 'not-allowed' : 'pointer',
            }}>
            <Zap size={14} />
            {running ? 'Forming Cluster...' : 'Simulate Cluster Formation'}
          </button>

          {/* Cluster Stats */}
          {phase >= 4 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-4">
              <div className="text-xs font-semibold text-nebula-green mb-3">✅ Cluster Online</div>
              <div className="space-y-2 text-xs">
                {[
                  { label: 'Nodes', value: nodes.length },
                  { label: 'Total RAM', value: `${nodes.reduce((a, n) => a + (n.ram_gb || 0), 0)}GB` },
                  { label: 'GPU Nodes', value: nodes.filter(n => n.node_type === 'gpu').length },
                  { label: 'Governor', value: nodes[0]?.name || 'Atlas' },
                ].map(({ label, value }) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-nebula-text-dim">{label}</span>
                    <span className="text-nebula-cyan font-mono">{value}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
