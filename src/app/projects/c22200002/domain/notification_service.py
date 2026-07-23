
from typing import Optional

from app.projects.c22200002.domain.models.notification import Notification
from app.projects.c22200002.domain.ports import IFCMClient, INotificationRepository

class NotificationService:

    def __init__(self, repo: INotificationRepository, fcm_client: IFCMClient) -> None:
        self._repo = repo
        self._fcm = fcm_client

    async def send(
        self,
        user_id: str,
        token: str,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> Notification:
        notification = await self._repo.create({
            "user_id": user_id,
            "token": token,
            "title": title,
            "body": body,
            "data": data,
        })

        try:
            await self._fcm.send_notification(token=token, title=title, body=body, data=data)
        except Exception as exc:
            await self._repo.mark_failed(notification.id, str(exc))
            return notification.model_copy(update={"status": "failed", "error": str(exc)})

        await self._repo.mark_sent(notification.id)
        return notification.model_copy(update={"status": "sent"})
