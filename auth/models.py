from re import L
from typing import List, Set, Optional

from pydantic import BaseModel
from fastapi_users import models


class User(models.BaseUser):
    tracked: List[str] = []
    is_active: bool = False


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


class UserList(BaseModel):
    users: List[User]
