import { Routes, Route } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import NodeMap from './pages/NodeMap.jsx'
import AIChat from './pages/AIChat.jsx'
import ClusterFormation from './pages/ClusterFormation.jsx'
import TrainingMonitor from './pages/TrainingMonitor.jsx'
import TrustLeaderboard from './pages/TrustLeaderboard.jsx'
import ExperimentReplay from './pages/ExperimentReplay.jsx'
import RealDistributedTraining from './pages/RealDistributedTraining.jsx'

export default function App() {
  const wsRef = useRef(null)

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/ws')
      wsRef.current = ws
      ws.onopen = () => {
        // ping every 20s to keep alive
        const interval = setInterval(() => ws.readyState === 1 && ws.send(JSON.stringify({ type: 'ping' })), 20000)
        ws.onclose = () => clearInterval(interval)
      }
      ws.onclose = () => setTimeout(connect, 3000) // auto-reconnect
    }
    connect()
    return () => wsRef.current?.close()
  }, [])

  return (
    <div className="flex min-h-screen nebula-bg">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/node-map" element={<NodeMap />} />
          <Route path="/ai-chat" element={<AIChat />} />
          <Route path="/cluster" element={<ClusterFormation />} />
          <Route path="/training" element={<TrainingMonitor />} />
          <Route path="/trust" element={<TrustLeaderboard />} />
          <Route path="/experiments" element={<ExperimentReplay />} />
          <Route path="/real-training" element={<RealDistributedTraining />} />
        </Routes>
      </main>
    </div>
  )
}
