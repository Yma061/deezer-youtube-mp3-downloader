#!/usr/bin/env python3
"""
Playlist Manager - Serveur Desktop
Lancement : python server.py
Interface  : http://localhost:8888
"""
import asyncio
import json
import os
import socket
import time
import webbrowser
from pathlib import Path

import yt_dlp
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel
from zeroconf import ServiceInfo, Zeroconf
from zeroconf.asyncio import AsyncZeroconf

# ── Config ────────────────────────────────────────────────────────────────────

MUSIC_DIR = Path.home() / "PlaylistManager"
MUSIC_DIR.mkdir(exist_ok=True)
PORT = 8888

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Playlist Manager Desktop")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Suivi des téléchargements en cours
_jobs: dict[str, dict] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def yt_base_opts() -> dict:
    return {"quiet": True}


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/library")
def get_library():
    """Retourne la liste de toutes les playlists et pistes."""
    playlists = []
    for pl_dir in sorted(MUSIC_DIR.iterdir()):
        if not pl_dir.is_dir():
            continue
        tracks = [
            {"name": f.stem, "file": f.name, "size": f.stat().st_size}
            for f in sorted(pl_dir.glob("*.mp3"))
        ]
        if tracks:
            playlists.append({"name": pl_dir.name, "tracks": tracks})
    return playlists


@app.get("/music/{playlist}/{filename}")
def serve_track(playlist: str, filename: str):
    """Sert un fichier MP3 au téléphone."""
    path = MUSIC_DIR / playlist / filename
    if not path.exists():
        return HTMLResponse("Not found", status_code=404)
    return FileResponse(str(path), media_type="audio/mpeg",
                        headers={"Accept-Ranges": "bytes"})


class DownloadRequest(BaseModel):
    url: str
    playlist_name: str = ""


@app.post("/api/download")
async def start_download(req: DownloadRequest):
    """Lance un téléchargement YouTube en arrière-plan."""
    job_id = str(time.time_ns())
    _jobs[job_id] = {"status": "running", "done": 0, "total": 0, "current": ""}
    asyncio.create_task(_download_task(job_id, req.url.strip(), req.playlist_name.strip()))
    return {"job_id": job_id}


@app.get("/api/progress/{job_id}")
async def stream_progress(job_id: str):
    """SSE : pousse l'état du job en temps réel."""
    async def generate():
        while True:
            p = _jobs.get(job_id, {"status": "unknown"})
            yield f"data: {json.dumps(p)}\n\n"
            if p.get("status") in ("done", "error"):
                break
            await asyncio.sleep(0.4)
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/jobs")
def list_jobs():
    return _jobs


# ── Tâche de téléchargement ───────────────────────────────────────────────────

async def _download_task(job_id: str, url: str, playlist_name: str):
    try:
        base = yt_base_opts()

        # 1. Récupérer les métadonnées de la playlist
        info_opts = {**base, "extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, False)

        entries = (info or {}).get("entries", [])
        if not entries:
            _jobs[job_id] = {"status": "error", "current": "Aucune vidéo trouvée."}
            return

        pl_name = playlist_name or (info or {}).get("title", "playlist")
        out_dir = MUSIC_DIR / pl_name
        out_dir.mkdir(exist_ok=True)

        _jobs[job_id]["total"] = len(entries)

        # 2. Progress hook : mis à jour à chaque fichier terminé
        finished = [0]
        def _hook(d: dict):
            if d["status"] == "finished":
                finished[0] += 1
                title = Path(d.get("filename", "")).stem
                _jobs[job_id].update({"done": finished[0], "current": title})

        # 3. Téléchargement playlist en une seule passe → %(playlist_index)s correct
        dl_opts = {
            **base,
            "format": "bestaudio/best",
            "outtmpl": str(out_dir / "%(playlist_index)02d - %(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "progress_hooks": [_hook],
        }
        with yt_dlp.YoutubeDL(dl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])

        _jobs[job_id]["status"]  = "done"
        _jobs[job_id]["current"] = f"{finished[0]} titres téléchargés dans « {pl_name} »"

    except Exception as exc:
        _jobs[job_id] = {"status": "error", "current": str(exc)}


# ── Interface Web ─────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Playlist Manager</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;padding:24px}
  h1{font-size:1.5rem;font-weight:700;margin-bottom:24px;color:#4ade80}
  .card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:20px}
  .card h2{font-size:1rem;font-weight:600;margin-bottom:12px;color:#94a3b8}
  input{width:100%;padding:10px 14px;border-radius:8px;border:1px solid #334155;
        background:#0f172a;color:#e2e8f0;font-size:14px;outline:none}
  input:focus{border-color:#4ade80}
  button{padding:10px 20px;border-radius:8px;border:none;cursor:pointer;font-weight:600;font-size:14px}
  .btn-green{background:#4ade80;color:#0f172a}
  .btn-green:hover{background:#22c55e}
  .btn-green:disabled{opacity:.5;cursor:not-allowed}
  .row{display:flex;gap:10px;margin-top:10px}
  .progress-box{margin-top:14px;padding:12px;background:#0f172a;border-radius:8px;display:none}
  .bar-bg{background:#334155;border-radius:4px;height:8px;margin:8px 0}
  .bar{background:#4ade80;height:8px;border-radius:4px;transition:width .3s}
  .status{font-size:13px;color:#94a3b8;margin-top:4px}
  .playlist{margin-bottom:12px}
  .pl-header{font-weight:600;color:#4ade80;margin-bottom:4px}
  .track{font-size:13px;color:#94a3b8;padding:2px 0 2px 12px}
  .empty{color:#475569;font-size:14px;text-align:center;padding:20px}
  .ip-badge{display:inline-block;background:#1e3a5f;color:#60a5fa;
            padding:6px 14px;border-radius:20px;font-size:13px;font-family:monospace}
</style>
</head>
<body>
<h1>🎵 Playlist Manager</h1>

<div class="card">
  <h2>Connexion depuis le téléphone</h2>
  <p style="font-size:13px;color:#94a3b8;margin-bottom:10px">
    Ouvrez l'application sur votre téléphone et tapez cette adresse :<br>
    (ou laissez l'app la détecter automatiquement via Wi-Fi)
  </p>
  <span class="ip-badge" id="ip-badge">Chargement...</span>
</div>

<div class="card">
  <h2>Télécharger une playlist YouTube</h2>
  <input id="url" type="url" placeholder="https://www.youtube.com/playlist?list=...">
  <div class="row">
    <input id="plname" type="text" placeholder="Nom de la playlist (optionnel)" style="flex:1">
    <button class="btn-green" id="dl-btn" onclick="startDownload()">Télécharger</button>
  </div>
  <div class="progress-box" id="prog-box">
    <div class="status" id="prog-status">Démarrage...</div>
    <div class="bar-bg"><div class="bar" id="prog-bar" style="width:0%"></div></div>
    <div class="status" id="prog-current"></div>
  </div>
</div>

<div class="card">
  <h2>Bibliothèque locale</h2>
  <div id="library"><div class="empty">Chargement...</div></div>
</div>

<script>
async function loadIp() {
  const r = await fetch('/api/ip');
  const d = await r.json();
  document.getElementById('ip-badge').textContent = d.ip + ':8888';
}

async function loadLibrary() {
  const r = await fetch('/api/library');
  const data = await r.json();
  const el = document.getElementById('library');
  if (!data.length) { el.innerHTML = '<div class="empty">Aucune playlist. Téléchargez-en une ci-dessus.</div>'; return; }
  el.innerHTML = data.map(pl => `
    <div class="playlist">
      <div class="pl-header">📁 ${pl.name} (${pl.tracks.length} titres)</div>
      ${pl.tracks.map(t => `<div class="track">🎵 ${t.name}</div>`).join('')}
    </div>`).join('');
}

async function startDownload() {
  const url = document.getElementById('url').value.trim();
  const name = document.getElementById('plname').value.trim();
  if (!url || !url.includes('youtube.com/playlist')) {
    alert('URL de playlist YouTube invalide.'); return;
  }
  const btn = document.getElementById('dl-btn');
  btn.disabled = true;
  const box = document.getElementById('prog-box');
  box.style.display = 'block';
  document.getElementById('prog-status').textContent = 'Démarrage...';
  document.getElementById('prog-bar').style.width = '0%';
  document.getElementById('prog-current').textContent = '';

  const r = await fetch('/api/download', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url, playlist_name: name})
  });
  const {job_id} = await r.json();

  const es = new EventSource(`/api/progress/${job_id}`);
  es.onmessage = e => {
    const p = JSON.parse(e.data);
    const pct = p.total > 0 ? Math.round(p.done / p.total * 100) : 0;
    document.getElementById('prog-bar').style.width = pct + '%';
    document.getElementById('prog-status').textContent =
      p.total > 0 ? `${p.done} / ${p.total} (${pct}%)` : 'En cours...';
    document.getElementById('prog-current').textContent = p.current || '';
    if (p.status === 'done' || p.status === 'error') {
      es.close();
      btn.disabled = false;
      if (p.status === 'done') loadLibrary();
    }
  };
}

loadIp();
loadLibrary();
setInterval(loadLibrary, 10000);
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def web_ui():
    return HTML


@app.get("/api/ip")
def get_ip():
    return {"ip": get_local_ip()}


# ── mDNS ─────────────────────────────────────────────────────────────────────

async def start_mdns(ip: str, port: int):
    """Annonce le serveur sur le réseau local via mDNS (Bonjour)."""
    try:
        zc = AsyncZeroconf()
        info = ServiceInfo(
            "_playlist._tcp.local.",
            "PlaylistManager._playlist._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={"version": b"1"},
        )
        await zc.async_register_service(info)
        print(f"[mDNS] Annoncé sur le réseau : PlaylistManager @ {ip}:{port}")
        return zc, info
    except Exception as e:
        print(f"[mDNS] Avertissement (non bloquant) : {e}")
        return None, None


# ── Démarrage ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"  Playlist Manager Desktop")
    print(f"  Interface  : http://localhost:{PORT}")
    print(f"  Téléphone  : http://{ip}:{PORT}")
    print(f"{'='*50}\n")
    webbrowser.open(f"http://localhost:{PORT}")
    await start_mdns(ip, PORT)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
