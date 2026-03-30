import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Server, Activity, Cpu, Play } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchDistStatus, startDistTraining, resetDistTraining } from '../api'

export default function RealDistributedTraining() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  const pollStatus = async () => {
    try {
      const data = await fetchDistStatus()
      setStatus(data)
    } catch (e) {
      console.error('Failed to fetch dist status', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    pollStatus()
    const interval = setInterval(pollStatus, 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="p-8 text-white">Connecting to Coordinator...</div>
  if (!status) return <div className="p-8 text-white">Coordinator offline. Start backend.</div>

  const isTraining = status.status === 'training'
  const isDone = status.status === 'done'
  const activeWorkers = status.workers?.filter(w => w.active) || []

  return (
    <div className="flex-1 p-8 h-screen overflow-y-auto w-full max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <Zap size={28} className="text-yellow-400" />
          Real Distributed ML (LAN)
        </h1>
        <p className="text-nebula-text-secondary">
          Monitor actual PyTorch nodes (laptops) connecting over the network to jointly train a CNN on MNIST via FedAvg.
        </p>
      </div>

      {/* Controls */}
      <div className="glass-panel p-6 rounded-2xl mb-6 flex items-center justify-between border border-nebula-cyan/20">
        <div className="flex gap-8">
          <div>
            <div className="text-sm text-nebula-text-dim mb-1">Status</div>
            <div className="font-mono text-lg text-white capitalize flex items-center gap-2">
              <span className={`status-dot ${isTraining ? 'online animate-pulse' : isDone ? 'online' : 'bg-gray-500'}`} />
              {status.status}
            </div>
          </div>
          <div>
            <div className="text-sm text-nebula-text-dim mb-1">Global Round</div>
            <div className="font-mono text-lg text-white">{status.round} <span className="text-nebula-text-dim text-sm">/ {status.target_rounds}</span></div>
          </div>
          <div>
            <div className="text-sm text-nebula-text-dim mb-1">Global Accuracy</div>
            <div className="font-mono text-lg text-green-400">{status.global_acc ? `${status.global_acc}%` : '--'}</div>
          </div>
        </div>

        <div className="flex gap-4">
          <button 
            onClick={() => resetDistTraining().then(pollStatus)}
            className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors"
          >
            Reset
          </button>
          <button 
            onClick={() => startDistTraining(20, 50).then(pollStatus)}
            disabled={activeWorkers.length === 0 || isTraining}
            className="px-6 py-2 rounded-lg bg-nebula-cyan text-black font-bold hover:shadow-[0_0_15px_rgba(0,212,255,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Play size={16} fill="currentColor" />
            Start Training
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workers List */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-bold text-white mb-4">Connected Laptops ({activeWorkers.length})</h2>
          
          {status.workers?.map(w => (
            <motion.div 
              key={w.worker_id}
              className={`glass-panel p-4 rounded-xl border ${w.active ? 'border-green-500/30' : 'border-red-500/30 opacity-50'}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <Server size={16} className={w.active ? 'text-green-400' : 'text-red-400'} />
                  <span className="font-bold text-white">{w.name}</span>
                </div>
                <div className="text-xs font-mono text-blue-300 bg-blue-900/30 px-2 py-1 rounded">id:{w.worker_id}</div>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-nebula-text-dim">IP Address</span>
                  <span className="text-white font-mono">{w.ip}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nebula-text-dim">Last Loss</span>
                  <span className="text-yellow-400 font-mono">{w.last_loss ? w.last_loss.toFixed(4) : '--'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-nebula-text-dim">CPU Load</span>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-mono">{w.cpu ? w.cpu.toFixed(1) : '--'}%</span>
                    <Cpu size={14} className="text-nebula-text-dim" />
                  </div>
                </div>
              </div>

              {isTraining && status.waiting_for?.includes(w.worker_id) && (
                <div className="mt-3 text-xs text-yellow-400 animate-pulse text-center bg-yellow-400/10 py-1 rounded">
                  Training local round...
                </div>
              )}
            </motion.div>
          ))}

          {status.workers?.length === 0 && (
            <div className="text-center p-8 border border-dashed border-white/20 rounded-xl text-nebula-text-dim">
              No workers connected.<br/>Run `START_WORKER.sh` on a laptop.
            </div>
          )}
        </div>

        {/* Loss Graph */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-white/5">
          <h2 className="text-xl font-bold text-white mb-6">Global Model Convergence</h2>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={status.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis 
                  dataKey="round" 
                  stroke="rgba(255,255,255,0.4)"
                  tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  padding={{ left: 10, right: 10 }}
                />
                <YAxis 
                  yAxisId="left"
                  stroke="rgba(255,255,255,0.4)"
                  tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#080810', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '12px' }}
                  itemStyle={{ fontFamily: 'monospace' }}
                />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="loss" 
                  stroke="#00d4ff" 
                  strokeWidth={3}
                  dot={{ fill: '#080810', stroke: '#00d4ff', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, fill: '#00d4ff' }}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
