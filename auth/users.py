from typing import Optional
import asyncio
import random

from fastapi import Depends, Request, APIRouter, Response, WebSocket
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import MongoDBUserDatabase

from db import get_user_db, db, redis
from .models import User, UserCreate, UserDB, UserUpdate, UserList

SECRET = "SECRET"


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: MongoDBUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 60 * 3)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_active_user = fastapi_users.current_user(active=True)

"""Updated"""

router = APIRouter()


@router.get("/", tags=["users"])
async def get_users(
    limit: int = 100, current_user: User = Depends(fastapi_users.current_user())
):
    if current_user.is_superuser:
        users = db["users"].find({}, {"_id": 0})
        users_list = await users.to_list(length=limit)
        return {"users": users_list}
    return f"Только для администратора"


@router.get("/tracked/{figi}", tags=["users"])
async def switch_tracked(
    figi: str, current_user: User = Depends(fastapi_users.current_user())
):
    if figi not in current_user.tracked:
        await db["users"].update_one(
            {"id": current_user.id}, {"$push": {"tracked": figi}}
        )
    else:
        await db["users"].update_one(
            {"id": current_user.id}, {"$pull": {"tracked": figi}}
        )

    updated_user = await db["users"].find_one({"id": current_user.id}, {"_id": 0})
    return updated_user
