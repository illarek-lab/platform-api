from motor.motor_asyncio import AsyncIOMotorClient

from app.projects.layout_example.config.settings import settings


class MongoDB:

    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DATABASE]


mongo = MongoDB()

database = mongo.db