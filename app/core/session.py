import uuid
from fastapi import Request, Response, HTTPException
from uuid import UUID
from app.core.redis import rdb

SESSION_EXPIRE_SECONDS = 60 * 30


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


async def get_current_user(request: Request) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail=[{"msg": "로그인이 필요합니다."}])

    user_id = await rdb.get(session_id)
    if not user_id:
        raise HTTPException(
            status_code=401, detail=[{"msg": "세션이 만료되었거나 존재하지 않습니다."}]
        )

    await rdb.expire(session_id, SESSION_EXPIRE_SECONDS)  # 세션 연장
    user_id_str = user_id.decode() if isinstance(user_id, bytes) else user_id
    return UUID(user_id_str)


async def destroy_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await rdb.delete(session_id)
        response.delete_cookie("session_id")
