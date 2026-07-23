from pymongo import AsyncMongoClient

from app.projects.c22200045.infra.settings import settings


class MongoDB:

    def __init__(self) -> None:
        self.client = AsyncMongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DATABASE]


mongo = MongoDB()
database = mongo.db