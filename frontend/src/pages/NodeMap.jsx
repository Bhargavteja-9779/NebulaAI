import { useState, useCallback, useEffect } from 'react'
import ReactFlow, {
  Background, Controls, MiniMap,
  addEdge, useNodesState, useEdgesState,
  MarkerType
} from 'reactflow'
import 'reactflow/dist/style.css'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { fetchNodes, simulateFailure, simulateRecovery } from '../api'
import { ZapOff, RefreshCw } from 'lucide-react'

const NODE_POSITIONS = [
  { x: 340, y: 60 },
  { x: 100, y: 200 },
  { x: 580, y: 200 },
  { x: 180, y: 380 },
  { x: 500, y: 380 },
]

const TRUST_COLORS = (score) => {
  if (score >= 85) return { bg: '#10b981', glow: 'rgba(16,185,129,0.5)' }
  if (score >= 70) return { bg: '#00d4ff', glow: 'rgba(0,212,255,0.5)' }
  if (score >= 50) return { bg: '#f59e0b', glow: 'rgba(245,158,11,0.5)' }
  return { bg: '#ef4444', glow: 'rgba(239,68,68,0.5)' }
}

const STATUS_COLORS = { online: '#10b981', offline: '#ef4444', busy: '#f59e0b' }

function CustomNode({ data }) {
  const colors = TRUST_COLORS(data.trust_score)
  return (
    <div className="relative" style={{ width: 110 }}>
      <div
        className="rounded-2xl p-4 text-center cursor-pointer transition-all duration-300"
        style={{
          background: '#13131f',
          border: `2px solid ${colors.bg}`,
          boxShadow: `0 0 20px ${colors.glow}`,
        }}
      >
        <div className="text-3xl mb-1">
          {data.node_type === 'gpu' ? '🖥️' : '💻'}
        </div>
        <div className="text-white text-xs font-bold">{data.label}</div>
        <div className="text-xs mt-1 font-mono" style={{ color: colors.bg }}>
          {data.trust_score?.toFixed(1)}
        </div>
        <div className="flex justify-center mt-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{
              background: STATUS_COLORS[data.status] || '#475569',
              boxShadow: `0 0 6px ${STATUS_COLORS[data.status] || '#475569'}`,
            }}
          />
        </div>
        <div className="text-[9px] mt-1" style={{ color: '#475569' }}>{data.location}</div>
      </div>
    </div>
  )
}

const nodeTypes = { compute: CustomNode }

export default function NodeMap() {
  const { data: apiNodes = [], refetch } = useQuery({ queryKey: ['nodes'], queryFn: fetchNodes })
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [event, setEvent] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!apiNodes.length) return
    const rfNodes = apiNodes.map((n, i) => ({
      id: String(n.id),
      type: 'compute',
      position: NODE_POSITIONS[i] || { x: Math.random() * 500, y: Math.random() * 300 },
      data: {
        label: n.name,
        trust_score: n.trust_score,
        status: n.status,
        node_type: n.node_type,
        location: n.location,
        nodeId: n.id,
      },
    }))
    setNodes(rfNodes)

    // Generate mesh edges
    const rfEdges = []
    for (let i = 0; i < rfNodes.length; i++) {
      for (let j = i + 1; j < rfNodes.length; j++) {
        if (Math.random() > 0.3) {
          rfEdges.push({
            id: `e${i}-${j}`,
            source: rfNodes[i].id,
            target: rfNodes[j].id,
            animated: true,
            style: { stroke: '#1e1e30', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#1e1e30' },
          })
        }
      }
    }
    setEdges(rfEdges)
  }, [apiNodes])

  const handleFailure = async (nodeId) => {
    if (loading) return
    setLoading(true)
    try {
      const res = await simulateFailure(nodeId)
      setEvent({ type: 'failure', msg: res.message, node: res.failed_node })
      setNodes(ns => ns.map(n =>
        n.data.nodeId === nodeId
          ? { ...n, data: { ...n.data, status: 'offline' } }
          : n
      ))
      setTimeout(() => refetch(), 1000)
    } finally {
      setLoading(false)
    }
  }

  const handleRecovery = async (nodeId) => {
    if (loading) return
    setLoading(true)
    try {
      const res = await simulateRecovery(nodeId)
      setEvent({ type: 'recovery', msg: res.message, node: res.node })
      setNodes(ns => ns.map(n =>
        n.data.nodeId === nodeId
          ? { ...n, data: { ...n.data, status: 'online' } }
          : n
      ))
      setTimeout(() => refetch(), 1000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 min-h-screen">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold text-nebula-text-primary mb-1">
          🌐 <span className="gradient-text">Node Network Map</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm">
          Live topology of all compute nodes. Color = trust tier. Animate = active link.
        </p>
      </motion.div>

      {/* Event Banner */}
      {event && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 px-4 py-3 rounded-xl text-sm font-medium"
          style={{
            background: event.type === 'failure' ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
            border: `1px solid ${event.type === 'failure' ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}`,
            color: event.type === 'failure' ? '#ef4444' : '#10b981',
          }}
        >
          {event.msg}
        </motion.div>
      )}

      <div className="grid grid-cols-4 gap-6">
        {/* React Flow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-card col-span-3"
          style={{ height: 480 }}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            style={{ background: 'transparent' }}
          >
            <svg style={{ position: 'absolute', width: 0, height: 0 }}>
              <defs>
                <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity="0.6" />
                </linearGradient>
              </defs>
            </svg>
            <Background color="#1e1e30" gap={24} size={1} />
            <Controls
              style={{ background: '#13131f', border: '1px solid #1e1e30', borderRadius: '8px' }}
            />
            <MiniMap
              style={{ background: '#0e0e1a', border: '1px solid #1e1e30' }}
              nodeColor={(n) => TRUST_COLORS(n.data?.trust_score || 50).bg}
            />
          </ReactFlow>
        </motion.div>

        {/* Node Controls */}
        <div className="space-y-3">
          <div className="text-xs font-semibold text-nebula-text-dim uppercase tracking-widest mb-3">
            Node Controls
          </div>
          {apiNodes.map(node => (
            <motion.div
              key={node.id}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card p-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <span className={`status-dot ${node.status}`} />
                <span className="text-sm font-medium text-nebula-text-primary">{node.name}</span>
              </div>
              <div className="text-xs text-nebula-text-dim mb-3">
                Trust: <span className="text-nebula-cyan font-mono">{node.trust_score.toFixed(1)}</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleFailure(node.id)}
                  disabled={loading || node.status === 'offline'}
                  className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-all"
                  style={{
                    background: 'rgba(239,68,68,0.1)',
                    border: '1px solid rgba(239,68,68,0.2)',
                    color: '#ef4444',
                    opacity: node.status === 'offline' ? 0.4 : 1,
                  }}
                >
                  <ZapOff size={11} /> Fail
                </button>
                <button
                  onClick={() => handleRecovery(node.id)}
                  disabled={loading || node.status === 'online'}
                  className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-all"
                  style={{
                    background: 'rgba(16,185,129,0.1)',
                    border: '1px solid rgba(16,185,129,0.2)',
                    color: '#10b981',
                    opacity: node.status === 'online' ? 0.4 : 1,
                  }}
                >
                  <RefreshCw size={11} /> Recover
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
