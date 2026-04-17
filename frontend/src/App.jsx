import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <ChatInterface />
    </div>
  )
}

export default App
