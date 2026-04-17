import { useState, useRef, useEffect } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am NeuroSearch AI. Ask me questions based on the ingested documents.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_BASE}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg, session_id: 'session-123' })
      });
      
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { role: 'ai', content: data.answer, sources: data.sources }]);
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: 'Error: ' + data.detail }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Connection error: ' + err.message }]);
    }
    
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`message-wrapper ${m.role}`}>
            <div className={`message ${m.role}`}>
              <div>{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="sources-container">
                  <strong>Sources:</strong>
                  <ul>
                    {m.sources.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message-wrapper ai">
            <div className="message ai">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <input 
            type="text" 
            className="chat-input" 
            placeholder="Ask about your knowledge base..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            className="send-btn" 
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
