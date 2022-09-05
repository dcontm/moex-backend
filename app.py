import asyncio
import pendulum
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import users
from auth.models import UserDB
from core import shares


app = FastAPI()


# need update for production
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    users.fastapi_users.get_auth_router(users.auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    users.fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_users_router(), prefix="/users", tags=["users"]
)
app.include_router(users.router, prefix="/users", tags=["users"])

app.include_router(
    shares.router,
    dependencies=[Depends(users.current_active_user)],
    prefix="/shares",
    tags=["shares"],
)


@app.on_event("startup")
async def startup_event():
    stream_redis = await asyncio.create_subprocess_exec(
        "python", "service_api.py", stdout=asyncio.subprocess.DEVNULL
    )
    print(f"Connect to Redis stream redis")


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(users.current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.get("/time")
async def world_time():
    moscow = pendulum.now("Europe/Moscow")
    london = pendulum.now("Europe/London")
    ny = pendulum.now("America/New_York")
    return {"Moscow": moscow, "London": london, "New-York": ny}
