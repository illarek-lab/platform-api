
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.projects.c22200002.domain.models.notification import Notification
from app.projects.c22200002.infra.db.mongo import database

_collection = database["notifications"]

class NotificationRepository:

    async def create(self, data: dict[str, Any]) -> Notification:
        doc = {
            **data,
            "status": "pending",
            "error": None,
            "created_at": datetime.now(timezone.utc),
            "sent_at": None,
        }
        result = await _collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return Notification.model_validate(doc)

    async def mark_sent(self, id: str) -> None:
        await _collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "sent", "sent_at": datetime.now(timezone.utc)}},
        )

    async def mark_failed(self, id: str, error: str) -> None:
        await _collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "failed", "error": error}},
        )
