import uuid
from fastapi import Request, Response, HTTPException
from uuid import UUID
from app.core.redis import rdb
from app.core.config import settings

SESSION_EXPIRE_SECONDS = settings.session_expire_seconds


def generate_session_id() -> str:
    return str(uuid.uuid4())


async def create_session(user_id: str, response: Response):
    session_id = generate_session_id()
    await rdb.setex(session_id, SESSION_EXPIRE_SECONDS, user_id)

    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        max_age=SESSION_EXPIRE_SECONDS,
        samesite="None",
        secure=True,
    )

    print(response.headers.get("set-cookie"))


async def get_current_user(request: Request, response: Response) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401)

    user_id = await rdb.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401)

    await rdb.expire(session_id, SESSION_EXPIRE_SECONDS)

    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        max_age=SESSION_EXPIRE_SECONDS,
        samesite="None",
        secure=True,
    )

    user_id_str = user_id.decode() if isinstance(user_id, bytes) else user_id
    return UUID(user_id_str)


async def destroy_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await rdb.delete(session_id)
        response.delete_cookie("session_id")
