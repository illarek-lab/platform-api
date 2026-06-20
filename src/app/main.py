import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.discovery import load_projects, registry

app = FastAPI(title="Platform API", version="1.0.0")

CREDENTIALS_DIR = Path(__file__).resolve().parents[2] / "credentials"
CREDENTIALS_DIR.mkdir(exist_ok=True)
TEMPLATE_FILE = CREDENTIALS_DIR / "layout_example.env"

print("STARTING APP")
load_projects(app)


def _parse_env(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            entries[key.strip()] = val.strip().strip('"').strip("'")
    return entries


_template_env = _parse_env(TEMPLATE_FILE.read_text()) if TEMPLATE_FILE.exists() else {}
_mongo_client = AsyncIOMotorClient(_template_env.get("MONGO_URI", ""))
_mongo_db = _mongo_client[_template_env.get("MONGO_DATABASE", "test")]
_students_col = _mongo_db["mobile_student_endpoint"]


def _safe_filename(name: str) -> str | None:
    if not name or ".." in name or "/" in name or "\\" in name:
        return None
    safe = re.sub(r"[^a-zA-Z0-9_\-.]", "_", name)
    if safe != name or not safe.endswith(".env"):
        return None
    return safe


@app.post("/credentials/upload", tags=["credentials"])
async def upload_credential(file: UploadFile):
    safe = _safe_filename(file.filename or "")
    if not safe:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Nombre inválido. Debe ser un archivo .env con solo letras, números, guiones y guiones bajos."
            },
        )

    content = await file.read()
    try:
        text = content.decode()
    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={"detail": "El archivo no es un archivo de texto válido."},
        )

    uploaded = _parse_env(text)
    required_keys = set(_template_env.keys())

    missing = sorted(required_keys - uploaded.keys())
    empty = sorted(k for k in required_keys & uploaded.keys() if not uploaded[k])

    errors: dict = {}
    if missing:
        errors["missing_keys"] = missing
    if empty:
        errors["empty_keys"] = empty
    if errors:
        total = len(missing) + len(empty)
        errors["detail"] = f"{total} campo(s) con problemas"
        return JSONResponse(status_code=400, content=errors)

    (CREDENTIALS_DIR / safe).write_bytes(content)

    project_name = safe.removesuffix(".env")
    await _students_col.update_one(
        {"project_name": project_name},
        {
            "$set": {
                "project_name": project_name,
                "filename": safe,
                "uploaded_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    return {"message": f"Archivo '{safe}' subido correctamente", "filename": safe}


@app.get("/credentials/students", tags=["credentials"])
async def list_students():
    cursor = _students_col.find({}, {"_id": 0}).sort("project_name", 1)
    students = await cursor.to_list(length=None)
    for s in students:
        if "uploaded_at" in s:
            s["uploaded_at"] = s["uploaded_at"].isoformat()
    return {"students": students}


@app.get("/credentials/ui", response_class=HTMLResponse, include_in_schema=False)
async def credentials_ui():
    cursor = _students_col.find({}, {"_id": 0}).sort("project_name", 1)
    students = await cursor.to_list(length=None)
    file_rows = ""
    for s in students:
        dt = s.get("uploaded_at")
        date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "—"
        name = s["filename"]
        file_rows += f"""
        <tr>
          <td class="file-name"><span class="file-icon">&#128196;</span> {name}</td>
          <td class="file-date">{date_str}</td>
        </tr>"""

    if not students:
        file_rows = '<tr><td colspan="2" class="empty">No hay credenciales registradas</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Subir Credentials — Illarek Lab</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a202c; min-height: 100vh; }}

  .topbar {{ background: #fff; border-bottom: 1px solid #e2e8f0; padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 62px; box-shadow: 0 1px 4px rgba(0,0,0,.04); }}
  .topbar-brand {{ display: flex; align-items: center; gap: 10px; text-decoration: none; }}
  .brand-logo {{ width: 30px; height: 30px; background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; }}
  .brand-logo svg {{ width: 16px; height: 16px; fill: #fff; }}
  .brand-text {{ display: flex; flex-direction: column; line-height: 1; }}
  .brand-name {{ font-size: 0.92rem; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }}
  .brand-sub {{ font-size: 0.65rem; font-weight: 500; color: #94a3b8; letter-spacing: .04em; text-transform: uppercase; margin-top: 1px; }}
  .topbar-links {{ display: flex; gap: 8px; }}
  .topbar-links a {{ font-size: 0.78rem; font-weight: 600; color: #0369a1; text-decoration: none; border: 1px solid #bae6fd; background: #f0f9ff; border-radius: 7px; padding: 5px 14px; transition: background .15s; }}
  .topbar-links a:hover {{ background: #e0f2fe; }}

  .container {{ max-width: 700px; margin: 48px auto; padding: 0 24px; }}
  h1 {{ font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-bottom: 8px; }}
  .subtitle {{ color: #64748b; font-size: 0.9rem; margin-bottom: 32px; }}

  .upload-zone {{ background: #fff; border: 2px dashed #cbd5e1; border-radius: 14px; padding: 40px; text-align: center; transition: border-color .2s, background .2s; cursor: pointer; margin-bottom: 32px; }}
  .upload-zone:hover, .upload-zone.dragover {{ border-color: #0ea5e9; background: #f0f9ff; }}
  .upload-zone svg {{ width: 48px; height: 48px; stroke: #94a3b8; margin-bottom: 12px; }}
  .upload-zone p {{ color: #64748b; font-size: 0.88rem; margin-bottom: 16px; }}
  .upload-zone .btn-upload {{ display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #0ea5e9, #0369a1); color: #fff; font-size: 0.88rem; font-weight: 700; border: none; border-radius: 8px; padding: 10px 24px; cursor: pointer; transition: transform .1s, box-shadow .2s; }}
  .upload-zone .btn-upload:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(14,165,233,.3); }}
  .upload-zone input[type="file"] {{ display: none; }}

  .files-card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.05); }}
  .files-header {{ padding: 14px 22px; border-bottom: 1px solid #f1f5f9; background: #fafbfc; font-size: 0.85rem; font-weight: 700; color: #0f172a; }}
  table {{ width: 100%; border-collapse: collapse; }}
  tr:not(:last-child) {{ border-bottom: 1px solid #f1f5f9; }}
  tr:hover {{ background: #f8fafc; }}
  td {{ padding: 12px 22px; font-size: 0.84rem; }}
  .file-name {{ display: flex; align-items: center; gap: 8px; color: #334155; font-family: "SF Mono", "Fira Code", monospace; }}
  .file-icon {{ font-size: 1rem; }}
  .file-date {{ text-align: right; color: #94a3b8; font-size: 0.78rem; white-space: nowrap; }}
  .empty {{ text-align: center; color: #94a3b8; padding: 24px; }}

  .error-panel {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 14px; padding: 0; margin-bottom: 24px; overflow: hidden; }}
  .error-panel-header {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; background: #fee2e2; border-bottom: 1px solid #fecaca; font-size: 0.88rem; font-weight: 700; color: #991b1b; }}
  .error-close {{ background: none; border: none; font-size: 1.2rem; color: #991b1b; cursor: pointer; padding: 0 4px; }}
  .error-section-title {{ font-size: 0.8rem; font-weight: 700; color: #b91c1c; padding: 10px 18px 4px; text-transform: uppercase; letter-spacing: .04em; }}
  .error-panel ul {{ list-style: none; padding: 4px 18px 12px; display: flex; flex-wrap: wrap; gap: 6px; }}
  .error-panel li {{ background: #fff; border: 1px solid #fecaca; color: #991b1b; font-family: "SF Mono", "Fira Code", monospace; font-size: 0.78rem; font-weight: 600; padding: 3px 10px; border-radius: 6px; }}

  .toast {{ position: fixed; bottom: 24px; right: 24px; background: #065f46; color: #fff; padding: 12px 20px; border-radius: 10px; font-size: 0.84rem; font-weight: 600; box-shadow: 0 4px 16px rgba(0,0,0,.15); opacity: 0; transform: translateY(10px); transition: all .3s; pointer-events: none; z-index: 999; }}
  .toast.show {{ opacity: 1; transform: translateY(0); }}
  .toast.error {{ background: #991b1b; }}

  footer {{ text-align: center; padding: 28px; font-size: 0.76rem; color: #94a3b8; margin-top: 48px; }}
  footer strong {{ color: #0369a1; }}
</style>
</head>
<body>

<div class="topbar">
  <a class="topbar-brand" href="/">
    <div class="brand-logo">
      <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
    </div>
    <div class="brand-text">
      <span class="brand-name">illarek-lab</span>
      <span class="brand-sub">Platform API</span>
    </div>
  </a>
  <div class="topbar-links">
    <a href="/">Dashboard</a>
    <a href="/docs">Swagger UI</a>
  </div>
</div>

<div class="container">
  <h1>Subir Credentials</h1>
  <p class="subtitle">Sube archivos <code>.env</code> al directorio <code>credentials/</code> del proyecto.</p>

  <div class="upload-zone" id="dropZone">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
    <p>Arrastra un archivo <strong>.env</strong> aquí o haz clic en el botón</p>
    <button class="btn-upload" onclick="document.getElementById('fileInput').click()">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      Subir Credentials
    </button>
    <input type="file" id="fileInput" accept=".env" />
  </div>

  <div id="errorPanel" class="error-panel" style="display:none;">
    <div class="error-panel-header">
      <span id="errorTitle"></span>
      <button class="error-close" onclick="document.getElementById('errorPanel').style.display='none'">&times;</button>
    </div>
    <div id="errorMissing" style="display:none;">
      <div class="error-section-title">Campos faltantes:</div>
      <ul id="missingList"></ul>
    </div>
    <div id="errorEmpty" style="display:none;">
      <div class="error-section-title">Campos sin valor:</div>
      <ul id="emptyList"></ul>
    </div>
  </div>

  <div class="files-card">
    <div class="files-header">Credenciales registradas</div>
    <table id="filesTable">
      {file_rows}
    </table>
  </div>
</div>

<div class="toast" id="toast"></div>

<footer>
  <strong>illarek-lab</strong> &mdash; Platform API &middot; Credentials Manager
</footer>

<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const toast = document.getElementById('toast');

function showToast(msg, isError) {{
  toast.textContent = msg;
  toast.className = 'toast show' + (isError ? ' error' : '');
  setTimeout(() => toast.className = 'toast', 3000);
}}

dropZone.addEventListener('dragover', e => {{ e.preventDefault(); dropZone.classList.add('dragover'); }});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {{
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
}});

fileInput.addEventListener('change', () => {{
  if (fileInput.files.length) uploadFile(fileInput.files[0]);
}});

function showErrors(data) {{
  const panel = document.getElementById('errorPanel');
  const missingDiv = document.getElementById('errorMissing');
  const emptyDiv = document.getElementById('errorEmpty');
  const missingList = document.getElementById('missingList');
  const emptyList = document.getElementById('emptyList');

  document.getElementById('errorTitle').textContent = data.detail;
  missingList.innerHTML = '';
  emptyList.innerHTML = '';

  if (data.missing_keys && data.missing_keys.length) {{
    missingDiv.style.display = '';
    data.missing_keys.forEach(k => {{ missingList.innerHTML += '<li>' + k + '</li>'; }});
  }} else {{ missingDiv.style.display = 'none'; }}

  if (data.empty_keys && data.empty_keys.length) {{
    emptyDiv.style.display = '';
    data.empty_keys.forEach(k => {{ emptyList.innerHTML += '<li>' + k + '</li>'; }});
  }} else {{ emptyDiv.style.display = 'none'; }}

  panel.style.display = '';
}}

async function uploadFile(file) {{
  const form = new FormData();
  form.append('file', file);
  document.getElementById('errorPanel').style.display = 'none';
  try {{
    const res = await fetch('/credentials/upload', {{ method: 'POST', body: form }});
    const text = await res.text();
    let data;
    try {{ data = JSON.parse(text); }} catch(_) {{
      showToast('Error del servidor: ' + res.status + ' — ' + text.substring(0, 100), true);
      return;
    }}
    if (res.ok) {{
      showToast(data.message, false);
      setTimeout(() => location.reload(), 800);
    }} else if (data.missing_keys || data.empty_keys) {{
      showErrors(data);
    }} else {{
      showToast(data.detail || 'Error al subir', true);
    }}
  }} catch(err) {{
    showToast('Error de conexión: ' + err.message, true);
  }}
}}

</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing():
    cards = ""
    for project in registry:
        route_rows = "".join(
            f'<tr><td class="method {r.split()[0]}">{r.split()[0]}</td><td class="path">{project["prefix"]}{r.split(" ", 1)[1]}</td></tr>'
            for r in project["routes"]
        )
        cards += f"""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">
                    <svg viewBox="0 0 24 24" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
                </div>
                <h2>{project["name"]}</h2>
                <span class="badge">project</span>
                <div class="links">
                    <a href="{project["prefix"]}/health">health</a>
                    <a href="/docs">docs</a>
                </div>
            </div>
            <table>{route_rows}</table>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Illarek Lab — Platform API</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a202c; min-height: 100vh; }}

  /* Top bar */
  .topbar {{ background: #fff; border-bottom: 1px solid #e2e8f0; padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 62px; box-shadow: 0 1px 4px rgba(0,0,0,.04); }}
  .topbar-brand {{ display: flex; align-items: center; gap: 10px; text-decoration: none; }}
  .brand-logo {{ width: 30px; height: 30px; background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; }}
  .brand-logo svg {{ width: 16px; height: 16px; fill: #fff; }}
  .brand-text {{ display: flex; flex-direction: column; line-height: 1; }}
  .brand-name {{ font-size: 0.92rem; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }}
  .brand-sub {{ font-size: 0.65rem; font-weight: 500; color: #94a3b8; letter-spacing: .04em; text-transform: uppercase; margin-top: 1px; }}
  .topbar-links {{ display: flex; gap: 8px; }}
  .topbar-links a {{ font-size: 0.78rem; font-weight: 600; color: #0369a1; text-decoration: none; border: 1px solid #bae6fd; background: #f0f9ff; border-radius: 7px; padding: 5px 14px; transition: background .15s; }}
  .topbar-links a:hover {{ background: #e0f2fe; }}

  /* Hero */
  .hero {{ max-width: 860px; margin: 48px auto 0; padding: 0 24px 44px; }}
  .hero-tag {{ display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: #0369a1; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 99px; padding: 4px 12px; margin-bottom: 18px; }}
  .hero-tag-dot {{ width: 6px; height: 6px; background: #0ea5e9; border-radius: 50%; animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .4; }} }}
  .hero h1 {{ font-size: 2.1rem; font-weight: 800; color: #0f172a; line-height: 1.15; letter-spacing: -.03em; }}
  .hero h1 span {{ color: #0ea5e9; }}
  .hero p {{ margin-top: 10px; color: #64748b; font-size: 0.93rem; }}
  .hero-stats {{ display: flex; gap: 24px; margin-top: 24px; }}
  .stat {{ display: flex; flex-direction: column; }}
  .stat-value {{ font-size: 1.4rem; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }}
  .stat-label {{ font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; margin-top: 1px; }}
  .stat-divider {{ width: 1px; background: #e2e8f0; }}

  /* Grid */
  .grid {{ max-width: 860px; margin: 0 auto; padding: 0 24px 60px; display: grid; gap: 16px; }}

  /* Card */
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.05); }}
  .card-header {{ padding: 16px 22px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; gap: 12px; background: #fafbfc; }}
  .card-icon {{ width: 32px; height: 32px; background: linear-gradient(135deg, #0ea5e9, #0369a1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .card-icon svg {{ width: 15px; height: 15px; fill: #fff; }}
  .card-header h2 {{ font-size: 0.92rem; font-weight: 700; color: #0f172a; flex: 1; }}
  .badge {{ font-size: 0.67rem; font-weight: 700; background: #f0f9ff; color: #0369a1; padding: 2px 9px; border-radius: 99px; text-transform: uppercase; letter-spacing: .06em; border: 1px solid #bae6fd; }}
  .links {{ display: flex; gap: 8px; }}
  .links a {{ font-size: 0.75rem; font-weight: 600; color: #059669; text-decoration: none; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 3px 10px; }}
  .links a:hover {{ background: #dcfce7; }}

  /* Table */
  table {{ width: 100%; border-collapse: collapse; }}
  tr {{ transition: background .1s; }}
  tr:hover {{ background: #f8fafc; }}
  tr:not(:last-child) {{ border-bottom: 1px solid #f1f5f9; }}
  td {{ padding: 9px 22px; font-size: 0.81rem; font-family: "SF Mono", "Fira Code", ui-monospace, monospace; }}
  .method {{ width: 66px; font-weight: 700; }}
  .method.GET {{ color: #059669; }}
  .method.POST {{ color: #2563eb; }}
  .method.PUT {{ color: #d97706; }}
  .method.DELETE {{ color: #dc2626; }}
  .method.PATCH {{ color: #7c3aed; }}
  .path {{ color: #475569; }}

  /* Footer */
  footer {{ text-align: center; padding: 28px; font-size: 0.76rem; color: #94a3b8; border-top: 1px solid #e2e8f0; background: #fff; margin-top: 8px; }}
  footer strong {{ color: #0369a1; }}
</style>
</head>
<body>

<div class="topbar">
  <a class="topbar-brand" href="/">
    <div class="brand-logo">
      <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
    </div>
    <div class="brand-text">
      <span class="brand-name">illarek-lab</span>
      <span class="brand-sub">Platform API</span>
    </div>
  </a>
  <div class="topbar-links">
    <a href="/credentials/ui">Subir Credentials</a>
    <a href="/docs">Swagger UI</a>
    <a href="/redoc">ReDoc</a>
  </div>
</div>

<div class="hero">
  <div class="hero-tag">
    <div class="hero-tag-dot"></div>
    Live &mdash; REST API
  </div>
  <h1>Illarek Lab<br><span>Platform API</span></h1>
  <p>Multi-project FastAPI platform. Projects are auto-discovered on startup.</p>
  <div class="hero-stats">
    <div class="stat">
      <span class="stat-value">{len(registry)}</span>
      <span class="stat-label">Project{"s" if len(registry) != 1 else ""}</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat">
      <span class="stat-value">{sum(len(p["routes"]) for p in registry)}</span>
      <span class="stat-label">Endpoints</span>
    </div>
  </div>
</div>

<div class="grid">{cards}</div>

<footer>
  <strong>illarek-lab</strong> &mdash; Platform API &middot; FastAPI &middot; Python
</footer>
</body>
</html>"""


@app.api_route("/{path:path}", methods=["GET"], include_in_schema=False)
async def catch_all(request: Request):
    return HTMLResponse(
        status_code=404,
        content=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 — Illarek Lab</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a202c; min-height: 100vh; display: flex; flex-direction: column; }}
  .topbar {{ background: #fff; border-bottom: 1px solid #e2e8f0; padding: 0 40px; display: flex; align-items: center; justify-content: space-between; height: 62px; box-shadow: 0 1px 4px rgba(0,0,0,.04); }}
  .topbar-brand {{ display: flex; align-items: center; gap: 10px; text-decoration: none; }}
  .brand-logo {{ width: 30px; height: 30px; background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; }}
  .brand-logo svg {{ width: 16px; height: 16px; fill: #fff; }}
  .brand-text {{ display: flex; flex-direction: column; line-height: 1; }}
  .brand-name {{ font-size: 0.92rem; font-weight: 800; color: #0f172a; letter-spacing: -.02em; }}
  .brand-sub {{ font-size: 0.65rem; font-weight: 500; color: #94a3b8; letter-spacing: .04em; text-transform: uppercase; margin-top: 1px; }}
  .content {{ flex: 1; display: flex; align-items: center; justify-content: center; }}
  .box {{ text-align: center; }}
  .code {{ font-size: 6rem; font-weight: 900; color: #0ea5e9; line-height: 1; letter-spacing: -.04em; }}
  .msg {{ font-size: 1.1rem; color: #64748b; margin-top: 8px; }}
  .back {{ display: inline-block; margin-top: 24px; font-size: 0.85rem; font-weight: 600; color: #0369a1; text-decoration: none; border: 1px solid #bae6fd; background: #f0f9ff; border-radius: 8px; padding: 8px 20px; transition: background .15s; }}
  .back:hover {{ background: #e0f2fe; }}
</style>
</head>
<body>
<div class="topbar">
  <a class="topbar-brand" href="/">
    <div class="brand-logo"><svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>
    <div class="brand-text"><span class="brand-name">illarek-lab</span><span class="brand-sub">Platform API</span></div>
  </a>
</div>
<div class="content">
  <div class="box">
    <div class="code">404</div>
    <p class="msg">La ruta <code>{request.url.path}</code> no existe.</p>
    <a class="back" href="/">Volver al inicio</a>
  </div>
</div>
</body>
</html>""",
    )
