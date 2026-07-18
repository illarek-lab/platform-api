import asyncio
import threading
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

from app.projects.c22200013.infra.settings import BASE_DIR, PROJECT_NAME

_CRED_DIR = BASE_DIR / "credentials_FMC"

_lock = threading.Lock()
_app: Optional[firebase_admin.App] = None


def _resolve_cred_path() -> Optional["object"]:
    """Ubica el JSON de la service account en credentials_FMC/.

    Prefiere el nombre convencional '<project>-firebase-adminsdk.json'; si no
    existe, acepta cualquier '*firebase-adminsdk*.json' (nombre por defecto que
    descarga Firebase Console).
    """
    preferred = _CRED_DIR / f"{PROJECT_NAME}-firebase-adminsdk.json"
    if preferred.exists():
        return preferred
    matches = sorted(_CRED_DIR.glob("*firebase-adminsdk*.json"))
    return matches[0] if matches else None


def _get_app() -> firebase_admin.App:
    """Inicializa la app de Firebase de forma perezosa (lazy).

    Así el proyecto se carga aunque todavía no exista el JSON de la service
    account; el error solo aparece al intentar enviar una notificación.
    """
    global _app
    if _app is not None:
        return _app
    with _lock:
        if _app is not None:
            return _app
        cred_path = _resolve_cred_path()
        if cred_path is None:
            raise RuntimeError(
                f"No se encontró la service account de Firebase en {_CRED_DIR}. "
                f"Coloca el JSON (idealmente '{PROJECT_NAME}-firebase-adminsdk.json') "
                "en el directorio credentials_FMC/."
            )
        _app = firebase_admin.initialize_app(
            credentials.Certificate(str(cred_path)),
            name=PROJECT_NAME,
        )
        return _app


class FirebaseClient:
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> str:
        app = _get_app()
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        return await asyncio.to_thread(messaging.send, message, app=app)


firebase_client = FirebaseClient()
