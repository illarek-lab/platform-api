from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.discovery import load_projects, registry

app = FastAPI(title="Platform API", version="1.0.0")

print("STARTING APP")
load_projects(app)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing():
    cards = ""
    for project in registry:
        route_rows = "".join(
            f'<tr><td class="method">{r.split()[0]}</td><td class="path">{project["prefix"]}{r.split(" ", 1)[1]}</td></tr>'
            for r in project["routes"]
        )
        cards += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge">project</span>
                <h2>{project["name"]}</h2>
                <div class="links">
                    <a href="{project["prefix"]}/health">health</a>
                    <a href="/docs#{project["name"]}">docs</a>
                </div>
            </div>
            <table>{route_rows}</table>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Platform API</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; padding: 48px 24px; }}
  header {{ max-width: 900px; margin: 0 auto 40px; }}
  header h1 {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
  header p {{ color: #718096; margin-top: 6px; font-size: 0.95rem; }}
  .meta {{ display: flex; gap: 16px; margin-top: 14px; }}
  .meta a {{ font-size: 0.85rem; color: #63b3ed; text-decoration: none; border: 1px solid #2d3748; border-radius: 6px; padding: 4px 12px; }}
  .meta a:hover {{ background: #1a202c; }}
  .grid {{ max-width: 900px; margin: 0 auto; display: grid; gap: 20px; }}
  .card {{ background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px; overflow: hidden; }}
  .card-header {{ padding: 20px 24px 16px; border-bottom: 1px solid #2d3748; display: flex; align-items: center; gap: 12px; }}
  .card-header h2 {{ font-size: 1.1rem; font-weight: 600; color: #fff; flex: 1; }}
  .badge {{ font-size: 0.7rem; font-weight: 600; background: #2c5282; color: #90cdf4; padding: 2px 8px; border-radius: 99px; text-transform: uppercase; letter-spacing: .05em; }}
  .links {{ display: flex; gap: 10px; }}
  .links a {{ font-size: 0.8rem; color: #68d391; text-decoration: none; }}
  .links a:hover {{ text-decoration: underline; }}
  table {{ width: 100%; border-collapse: collapse; }}
  tr:not(:last-child) {{ border-bottom: 1px solid #1e2435; }}
  td {{ padding: 9px 24px; font-size: 0.85rem; font-family: "SF Mono", "Fira Code", monospace; }}
  .method {{ width: 72px; font-weight: 700; color: #f6ad55; }}
  .path {{ color: #a0aec0; }}
</style>
</head>
<body>
<header>
  <h1>Platform API</h1>
  <p>{len(registry)} project{"s" if len(registry) != 1 else ""} loaded</p>
  <div class="meta">
    <a href="/docs">Swagger UI</a>
    <a href="/redoc">ReDoc</a>
  </div>
</header>
<div class="grid">{cards}</div>
</body>
</html>"""
