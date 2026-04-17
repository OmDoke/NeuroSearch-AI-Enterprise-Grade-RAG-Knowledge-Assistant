import { useState } from 'react';

export default function Sidebar() {
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleUrlSubmit = async () => {
    if (!url) return;
    setLoading(true);
    setStatus(null);
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_BASE}/api/ingest/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (res.ok) setStatus({ type: 'success', msg: data.message });
      else setStatus({ type: 'error', msg: data.detail });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    }
    setLoading(false);
  };

  const handleFileUpload = async () => {
    if (!file) return;
    setLoading(true);
    setStatus(null);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_BASE}/api/ingest/file`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) setStatus({ type: 'success', msg: data.message });
      else setStatus({ type: 'error', msg: data.detail });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    }
    setLoading(false);
  };

  return (
    <div className="sidebar">
      <h1>
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="28" height="28">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        NeuroSearch
      </h1>
      
      <div className="ingest-section">
        <div className="ingest-card">
          <h3>Ingest Document (PDF)</h3>
          <input 
            type="file" 
            className="input-field" 
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button 
            className="btn" 
            onClick={handleFileUpload} 
            disabled={loading || !file}
          >
            {loading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </div>

        <div className="ingest-card">
          <h3>Ingest Web URL</h3>
          <input 
            type="text" 
            className="input-field" 
            placeholder="https://example.com/article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button 
            className="btn" 
            onClick={handleUrlSubmit}
            disabled={loading || !url}
          >
            {loading ? 'Processing...' : 'Process URL'}
          </button>
        </div>
      </div>

      {status && (
        <div className={`status-badge ${status.type}`}>
          {status.msg}
        </div>
      )}
    </div>
  );
}
