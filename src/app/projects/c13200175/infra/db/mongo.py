from motor.motor_asyncio import AsyncIOMotorClient

from app.projects.c13200175.infra.settings import settings


class MongoDB:

    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DATABASE]


mongo = MongoDB()
database = mongo.db
