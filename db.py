import os
import aioredis
import motor.motor_asyncio
from fastapi_users.db import MongoDBUserDatabase
from auth.models import UserDB


redis = aioredis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)


client = motor.motor_asyncio.AsyncIOMotorClient(
    os.environ.get("MONGODB_URL"), uuidRepresentation="standard"
)
db = client["moex"]


async def get_user_db():
    yield MongoDBUserDatabase(UserDB, db["users"])
