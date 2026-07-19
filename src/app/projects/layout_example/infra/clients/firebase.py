import asyncio
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

from app.projects.layout_example.infra.settings import BASE_DIR, PROJECT_NAME

logger = logging.getLogger(__name__)

_cred_path = BASE_DIR / "credentials_FMC" / f"{PROJECT_NAME}-firebase-adminsdk.json"
_app = None

if _cred_path.exists():
    try:
        _app = firebase_admin.initialize_app(credentials.Certificate(str(_cred_path)), name=PROJECT_NAME)
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
else:
    logger.warning(f"Firebase credentials file not found at {_cred_path}. FirebaseClient will fail on send.")


class FirebaseClient:

    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> str:
        global _app
        if _app is None:
            # Try to initialize again in case credentials were uploaded after startup
            if _cred_path.exists():
                try:
                    _app = firebase_admin.initialize_app(credentials.Certificate(str(_cred_path)), name=PROJECT_NAME)
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase Admin SDK on-demand: {e}")
                    raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {e}") from e
            else:
                raise RuntimeError(
                    f"Firebase Admin SDK is not initialized. Credential file {_cred_path} is missing or invalid."
                )

        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )
        return await asyncio.to_thread(messaging.send, message, app=_app)


firebase_client = FirebaseClient()
