from fastapi import FastAPI
from app.core.discovery import load_projects

app = FastAPI(title="Platform API", version="1.0.0")


# ─────────────────────────────
# Auto-load all projects
# ─────────────────────────────
print("STARTING APP")
load_projects(app)
