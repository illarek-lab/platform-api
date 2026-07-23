
import asyncio
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

from app.projects.c22200002.infra.settings import BASE_DIR, PROJECT_NAME

_cred_path = BASE_DIR / "credentials_FMC" / f"{PROJECT_NAME}-firebase-adminsdk.json"

_app = None

if _cred_path.exists():
    _app = firebase_admin.initialize_app(
        credentials.Certificate(str(_cred_path)),
        name=PROJECT_NAME,
    )

class FirebaseClient:
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> str:
        if _app is None:
            raise RuntimeError(
                f"Firebase credentials not configured: {_cred_path}"
            )

        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )

        return await asyncio.to_thread(messaging.send, message, app=_app)

firebase_client = FirebaseClient()
