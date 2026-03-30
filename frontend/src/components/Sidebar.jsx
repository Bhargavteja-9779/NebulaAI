import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, Network, MessageSquare, Activity,
  Shield, FlaskConical, Zap, GitBranch
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/node-map', icon: Network, label: 'Node Map' },
  { to: '/ai-chat', icon: MessageSquare, label: 'AI Orchestrator' },
  { to: '/cluster', icon: GitBranch, label: 'Cluster Formation' },
  { to: '/training', icon: Activity, label: 'Training Monitor' },
  { to: '/real-training', icon: Zap, label: 'Real Distributed ML' },
  { to: '/trust', icon: Shield, label: 'Trust Leaderboard' },
  { to: '/experiments', icon: FlaskConical, label: 'Experiment Replay' },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col z-50"
      style={{ background: 'rgba(8,8,16,0.95)', borderRight: '1px solid #1e1e30', backdropFilter: 'blur(20px)' }}>
      
      {/* Logo */}
      <div className="px-6 py-6 border-b border-nebula-border">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="relative w-9 h-9">
            <div className="absolute inset-0 rounded-xl animate-glow-pulse"
              style={{ background: 'linear-gradient(135deg, #00d4ff, #7c3aed)' }} />
            <div className="absolute inset-0.5 rounded-[10px] flex items-center justify-center"
              style={{ background: '#080810' }}>
              <Zap size={16} className="text-nebula-cyan" />
            </div>
          </div>
          <div>
            <div className="font-bold text-base gradient-text">NebulaAI</div>
            <div className="text-[10px] text-nebula-text-dim uppercase tracking-widest">Research Cloud</div>
          </div>
        </motion.div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map(({ to, icon: Icon, label }, i) => (
            <motion.div
              key={to}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                    isActive
                      ? 'bg-nebula-cyan/10 text-nebula-cyan border border-nebula-cyan/20'
                      : 'text-nebula-text-secondary hover:text-nebula-text-primary hover:bg-white/4'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={16} className={isActive ? 'text-nebula-cyan' : 'text-nebula-text-dim group-hover:text-nebula-text-secondary'} />
                    <span>{label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="nav-indicator"
                        className="ml-auto w-1.5 h-1.5 rounded-full bg-nebula-cyan"
                      />
                    )}
                  </>
                )}
              </NavLink>
            </motion.div>
          ))}
        </div>
      </nav>

      {/* Status Footer */}
      <div className="px-6 py-4 border-t border-nebula-border">
        <div className="flex items-center gap-2">
          <span className="status-dot online" />
          <span className="text-xs text-nebula-text-secondary">System Operational</span>
        </div>
        <div className="text-[10px] text-nebula-text-dim mt-1 font-mono">v1.0.0 · nebula.ai</div>
      </div>
    </aside>
  )
}
