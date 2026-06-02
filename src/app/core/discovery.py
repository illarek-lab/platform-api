import importlib
import pkgutil
from fastapi import FastAPI, APIRouter
from app.projects import __path__ as projects_path


def load_projects(app: FastAPI):

    for module_info in pkgutil.iter_modules(projects_path):

        module_name = module_info.name
        module_path = f"app.projects.{module_name}.router"

        try:
            module = importlib.import_module(module_path)

            router: APIRouter = getattr(module, "router", None)

            if router:
                app.include_router(router, prefix=f"/{module_name}", tags=[module_name])

                print(f"✔ Loaded project: {module_name}")

        except ModuleNotFoundError:
            print(f"⚠ No router found in {module_name}")
