from app.projects.layout_example.database.mongo.connection import database


class UserRepository:

    collection = database["mobile_users"]

    async def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    async def create_user(self, user: dict):
        return self.collection.insert_one(user)

    async def find_by_google_id(self, google_id: str):
        return self.collection.find_one({"google_id": google_id})


user_repo = UserRepository()
