'use client'
import { useEffect, useRef, useState } from 'react'

export default function Generator(){
  const envBase = process.env.NEXT_PUBLIC_API_BASE_URL
  const baseUrl = (envBase && envBase.length) ? envBase : 'http://127.0.0.1:8000'

  const [prompt, setPrompt] = useState('A beautiful landscape in painterly style')
  const [width, setWidth] = useState(512)
  const [height, setHeight] = useState(512)
  const [steps, setSteps] = useState(20)
  const [batch, setBatch] = useState(1)
  const [status, setStatus] = useState('idle')
  const [results, setResults] = useState([])
  const [errorMsg, setErrorMsg] = useState(null)
  const [loading, setLoading] = useState(false)
  const pollRef = useRef(null)

  useEffect(()=>{ return ()=>{ if(pollRef.current) clearInterval(pollRef.current) }},[])

  async function handleGenerate(){
    setErrorMsg(null); setResults([]); setLoading(true); setStatus('sending...')
    try{
      const payload = { prompt, width:+width, height:+height, steps:+steps, batch:+batch,
        provider:'replicate', base_url: envBase || 'http://127.0.0.1:8000' }

      const url = (baseUrl || '') + '/generate'
      const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) })
      if(!res.ok){ const text=await res.text().catch(()=>null); throw new Error(`Create job failed: ${res.status} ${res.statusText} ${text||''}`)}
      const data = await res.json()
      if(!data.job_id) throw new Error('No job_id in response')
      setStatus('queued: '+data.job_id); startPolling(data.job_id)
    }catch(err){ setErrorMsg(String(err.message||err)); setStatus('error'); setLoading(false) }
  }

  function startPolling(jobId){
    setStatus('running...'); setLoading(true)
    if(pollRef.current) clearInterval(pollRef.current)
    pollRef.current=setInterval(async()=>{
      try{
        const r=await fetch((baseUrl||'')+`/generate/${jobId}`)
        if(!r.ok){ const t=await r.text().catch(()=>null); throw new Error(`status fetch failed: ${r.status} ${r.statusText} ${t||''}`)}
        const j=await r.json(); setStatus(j.status)
        if(j.status==='success'){ clearInterval(pollRef.current); pollRef.current=null; setResults(j.images||[]); setLoading(false)}
        else if(['failed','aborted'].includes(j.status)){ clearInterval(pollRef.current); pollRef.current=null; setErrorMsg(j.error||'Job failed'); setLoading(false)}
      }catch(e){ setErrorMsg(String(e.message||e)); setStatus('poll error'); if(pollRef.current){clearInterval(pollRef.current);pollRef.current=null}; setLoading(false)}
    },2000)
  }

  return (
    <div className="page-bg">
      <div className="gen-root">
        {/* Banner */}
        <div className="banner">
          <div className="banner-inner">
            <h1 className="banner-title">✨ AI Image Generator</h1>
            <p className="banner-sub">Turn your imagination into visuals. Adjust size, steps, and batch for more control</p>
            <p className="banner-sub">Right click on the image once generated to download into your system</p>
          </div>
        </div>

        {/* Control card */}
        <div className="card">
          <div className="field">
            <label className="label">Prompt</label>
            <textarea className="textarea" value={prompt} onChange={e=>setPrompt(e.target.value)} />
          </div>

          <div className="grid">
            <div className="field small"><label className="label">Width</label>
              <input className="input" type="number" value={width} onChange={e=>setWidth(e.target.value)} /></div>
            <div className="field small"><label className="label">Height</label>
              <input className="input" type="number" value={height} onChange={e=>setHeight(e.target.value)} /></div>
            <div className="field small"><label className="label">Steps</label>
              <input className="input" type="number" value={steps} onChange={e=>setSteps(e.target.value)} /></div>
            <div className="field small"><label className="label">Batch</label>
              <input className="input" type="number" value={batch} onChange={e=>setBatch(e.target.value)} /></div>
          </div>

          <div className="actions">
            <button className="btn" onClick={handleGenerate} disabled={loading}>
              {loading ? '🎨 Generating...' : 'Generate Image'}
            </button>
            <div className="status">Status: <strong>{status}</strong></div>
          </div>

          {errorMsg && <div className="error"><strong>Error:</strong> {errorMsg}</div>}
        </div>

        {/* Results */}
        <div className="results-wrap">
          <h2 className="results-title">Gallery Results</h2>
          {results.length===0 && !loading && <p className="muted">No results yet. Generate your first masterpiece!</p>}
          <div className="results-grid">
            {results.map(img=>(
              <div className="result-card" key={img.image_id||img.url}>
                <div className="img-wrap"><img src={img.thumbnail||img.url} alt="generated"/></div>
                <div className="meta">{img.url}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="footer-note">
          <div>🔗 API endpoint: <code>{(baseUrl||'')+'/generate'}</code></div>
          <div className="muted">Backend must be running & CORS allowed.</div>
        </div>
      </div>
      <style jsx global>{`
          html, body {
            margin: 0;
            padding: 0;
            height: 100%;
          }
        `}</style>

      <style jsx>{`

        .page-bg {
          background: linear-gradient(135deg, #e2c3feff, #fde047, #facc15);
          min-height: 100vh;
          width: 100vw; /* full width */
          margin: 0;    /* remove browser gap */
          padding: 30px 0;
        }
        .gen-root {
          max-width: 980px;
          margin: 0 auto;
          padding: 0 20px; /* small padding instead of white gaps */
        }


        .banner {
          background: linear-gradient(90deg, #38bdf8, #06b6d4, #3b82f6);
          border-radius: 18px;
          padding: 32px;
          box-shadow: 0 8px 24px rgba(59,130,246,0.2);
          margin-bottom: 24px;
          color: #fff;
        }
        .banner-title { margin:0; font-size:30px; font-weight:700; }
        .banner-sub { margin-top:6px; font-size:15px; opacity:0.9; }

        .card {
          background: linear-gradient(180deg,#ffffff,#f9fafb);
          border-radius:14px;
          padding:20px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.05);
          border: 1px solid #e5e7eb;
          margin-bottom: 24px;
        }

        .field{margin-bottom:14px;}
        .label{font-size:13px;color:#334155;font-weight:600;margin-bottom:6px;display:block;}
        .textarea{
          width:100%;min-height:120px;padding:12px;border-radius:10px;
          border:1px solid #d1d5db;font-size:14px;resize:vertical;
          background:linear-gradient(180deg,#f8fafc,#f1f5f9);
        }
        .grid{display:flex;gap:12px;flex-wrap:wrap;}
        .field.small{flex:1 1 140px;min-width:140px;}
        .input{
          width:100%;padding:10px;border-radius:10px;border:1px solid #d1d5db;
          background:linear-gradient(180deg,#f9fafb,#f3f4f6);font-size:14px;
        }

        .actions{display:flex;align-items:center;gap:16px;margin-top:12px;}
        .btn{
          background:linear-gradient(90deg,#06b6d4,#3b82f6);
          border:none;color:#fff;padding:10px 20px;border-radius:30px;
          font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(59,130,246,0.25);
          transition:transform 0.1s ease-in-out;
        }
        .btn:hover{transform:translateY(-2px);}
        .btn:disabled{opacity:0.6;cursor:default;}
        .status{font-size:14px;color:#475569;}

        .error{margin-top:12px;color:#b91c1c;background:#fee2e2;padding:10px;border-radius:8px;}

        .results-wrap{margin-bottom:24px;}
        .results-title{font-size:20px;font-weight:600;margin-bottom:10px;color:#1e293b;}
        .muted{color:#64748b;}
        .results-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px;}
        .result-card{
          background:linear-gradient(180deg,#ffffff,#f9fafb);
          border-radius:12px;overflow:hidden;
          box-shadow:0 6px 18px rgba(0,0,0,0.06);border:1px solid #e5e7eb;
        }
        .img-wrap{width:100%;aspect-ratio:1.6/1;background:#f1f5f9;display:flex;align-items:center;justify-content:center;}
        .img-wrap img{width:100%;height:100%;object-fit:cover;}
        .meta{padding:10px;font-size:12px;color:#475569;word-break:break-all;}

        .footer-note{margin-top:24px;font-size:13px;color:#475569;}
        code{background:#f1f5f9;padding:2px 6px;border-radius:4px;}
      `}</style>
    </div>
  )
}
