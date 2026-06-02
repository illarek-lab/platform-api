import importlib
import pkgutil

import app.projects as projects
from fastapi import FastAPI


def _import_project_module(project_name: str):
    """Load project entry module (`router.py`)."""
    module_path = f"app.projects.{project_name}.api.router"
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None


def load_projects(app: FastAPI):

    print("🔍 Scanning projects...")

    print("PATH:", projects.__path__)

    for m in pkgutil.iter_modules(projects.__path__):
        print("FOUND MODULE:", m.name)

        try:
            module = _import_project_module(m.name)
            if module is None:
                print(f"⚠ No router.py in {m.name}")
                continue

            router = getattr(module, "router", None)

            if router:
                app.include_router(router, prefix=f"/{m.name}")
                print(f"✔ LOADED: {m.name}")
            else:
                print(f"⚠ No `router` object in {m.name}")

        except Exception as e:
            print(f"❌ ERROR {m.name}: {e}")
