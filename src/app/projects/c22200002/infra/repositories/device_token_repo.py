
from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument

from app.projects.c22200002.domain.models.device_token import DeviceToken
from app.projects.c22200002.infra.db.mongo import database

_collection = database["matching_user_tokenFMC"]

class DeviceTokenRepository:

    async def upsert(self, data: dict[str, Any]) -> DeviceToken:
        doc = await _collection.find_one_and_update(
            {"device_id": data["device_id"]},
            {"$set": {**data, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        doc["id"] = str(doc.pop("_id"))
        return DeviceToken.model_validate(doc)
