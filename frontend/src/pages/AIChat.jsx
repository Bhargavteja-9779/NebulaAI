import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, ChevronDown, ChevronUp, Zap, Clock, Target, Server } from 'lucide-react'
import { orchestrate } from '../api'

const SUGGESTIONS = [
  'Train the best model fast',
  'Run MNIST with high accuracy',
  'Train a ResNet on CIFAR-10',
  'Deploy a fast LSTM text classifier',
  'Build a transformer model',
]

function AgentStep({ step, delay }) {
  const [open, setOpen] = useState(false)
  const iconMap = { '🧠': '#7c3aed', '📡': '#00d4ff', '✅': '#10b981', '⚡': '#f59e0b', '🔄': '#ec4899' }
  const color = iconMap[step.icon] || '#94a3b8'
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="rounded-xl overflow-hidden"
      style={{ border: `1px solid rgba(${color === '#00d4ff' ? '0,212,255' : '124,58,237'},0.15)` }}
    >
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left"
        style={{ background: 'rgba(255,255,255,0.02)' }}
      >
        <span className="text-base">{step.icon}</span>
        <div className="flex-1">
          <div className="text-xs font-semibold" style={{ color }}>{step.agent} Agent</div>
          <div className="text-xs text-nebula-text-secondary">{step.action}</div>
        </div>
        <div className="text-[10px] text-nebula-text-dim font-mono">{step.duration_ms}ms</div>
        {open ? <ChevronUp size={12} className="text-nebula-text-dim" /> : <ChevronDown size={12} className="text-nebula-text-dim" />}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 text-xs text-nebula-text-secondary font-mono leading-relaxed"
              style={{ background: 'rgba(0,0,0,0.2)' }}>
              <div className="mb-1 text-nebula-text-dim">Reasoning:</div>
              {step.reasoning}
              <div className="mt-2 text-nebula-text-dim">Result:</div>
              <span style={{ color }}>{step.result_summary}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function ResultCard({ icon: Icon, label, value, color }) {
  return (
    <div className="flex-1 rounded-xl p-4 text-center"
      style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #1e1e30' }}>
      <Icon size={18} style={{ color, margin: '0 auto 6px' }} />
      <div className="text-sm font-bold" style={{ color }}>{value}</div>
      <div className="text-[10px] text-nebula-text-dim mt-1">{label}</div>
    </div>
  )
}

export default function AIChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Welcome to NebulaAI Orchestrator. Tell me what you want to train — I\'ll plan it, allocate nodes, and start training automatically.',
      type: 'greeting',
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const prompt = text || input.trim()
    if (!prompt || loading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', content: prompt }])
    setLoading(true)
    try {
      const res = await orchestrate({ prompt })
      setMessages(m => [...m, {
        role: 'assistant',
        type: 'result',
        content: res.reasoning,
        model: res.model_suggestion,
        nodes: res.node_allocation,
        time: res.time_estimate,
        accuracy: res.accuracy_prediction,
        chain: res.agent_chain,
        jobId: res.job_id,
      }])
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: '❌ Orchestration failed. Is the backend running?', type: 'error' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen p-8">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl font-bold">
          <span className="gradient-text">AI Orchestrator</span>
        </h1>
        <p className="text-nebula-text-secondary text-sm mt-1">
          Natural language → 5-agent pipeline → auto training. Just describe your goal.
        </p>
      </motion.div>

      {/* Suggestions */}
      <div className="flex gap-2 flex-wrap mb-4">
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => send(s)}
            className="px-3 py-1.5 rounded-lg text-xs text-nebula-text-secondary transition-all hover:text-nebula-cyan"
            style={{ background: 'rgba(0,212,255,0.05)', border: '1px solid rgba(0,212,255,0.1)' }}>
            {s}
          </button>
        ))}
      </div>

      {/* Chat */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg flex items-center justify-center mr-3 flex-shrink-0"
                  style={{ background: 'linear-gradient(135deg,#00d4ff,#7c3aed)' }}>
                  <Bot size={14} className="text-white" />
                </div>
              )}
              <div className={`max-w-2xl ${msg.role === 'user' ? 'ml-12' : 'mr-4'}`}>
                {msg.role === 'user' ? (
                  <div className="px-4 py-2.5 rounded-2xl rounded-tr-md text-sm"
                    style={{ background: 'linear-gradient(135deg,rgba(0,212,255,0.15),rgba(124,58,237,0.15))', border: '1px solid rgba(0,212,255,0.2)' }}>
                    {msg.content}
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="px-4 py-3 rounded-2xl rounded-tl-md text-sm text-nebula-text-secondary glass-card">
                      {msg.content}
                    </div>
                    {msg.type === 'result' && (
                      <>
                        {/* Result Cards */}
                        <div className="flex gap-3">
                          <ResultCard icon={Zap} label="Model" value={msg.model} color="#00d4ff" />
                          <ResultCard icon={Server} label="Nodes" value={msg.nodes?.length} color="#7c3aed" />
                          <ResultCard icon={Clock} label="ETA" value={msg.time} color="#f59e0b" />
                          <ResultCard icon={Target} label="Predicted Acc" value={msg.accuracy} color="#10b981" />
                        </div>
                        {/* Agent Chain */}
                        <div className="space-y-2">
                          <div className="text-[10px] uppercase tracking-wider text-nebula-text-dim px-1">
                            Agent Execution Chain
                          </div>
                          {msg.chain?.map((step, j) => (
                            <AgentStep key={j} step={step} delay={j * 0.08} />
                          ))}
                        </div>
                        {msg.jobId && (
                          <div className="text-xs text-nebula-cyan font-mono px-1">
                            ✅ Job #{msg.jobId} submitted. Monitor progress in Training tab →
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg flex items-center justify-center ml-3 flex-shrink-0"
                  style={{ background: '#1e1e30' }}>
                  <User size={14} className="text-nebula-text-secondary" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg,#00d4ff,#7c3aed)' }}>
              <Bot size={14} className="text-white" />
            </div>
            <div className="glass-card px-4 py-3 rounded-2xl">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <motion.div key={i} className="w-1.5 h-1.5 rounded-full bg-nebula-cyan"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 0.6, delay: i * 0.15, repeat: Infinity }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type your training request... (e.g. 'Train best model fast')"
          disabled={loading}
          className="flex-1 px-4 py-3 rounded-xl text-sm outline-none transition-all text-nebula-text-primary placeholder-nebula-text-dim"
          style={{ background: '#13131f', border: '1px solid #1e1e30' }}
          id="orchestrator-input"
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="px-4 py-3 rounded-xl flex items-center gap-2 text-sm font-medium transition-all"
          style={{ background: 'linear-gradient(135deg,#00d4ff,#7c3aed)', color: '#fff',
                   opacity: !input.trim() || loading ? 0.5 : 1 }}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
