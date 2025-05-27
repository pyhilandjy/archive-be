from app.config import settings
from fastapi import HTTPException
from app.db.worker import execute_insert_update_query, execute_select_query
from app.db.query import USER_LOGIN_DATA
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def user_login(email: str, password: str):
    """
    로그인 API - 이메일과 비밀번호로 사용자 인증
    """
    user = execute_select_query(
        USER_LOGIN_DATA,
        params={"email": email},
    )

    if not user:
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다."
        )

    user = user[0]
    if not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다."
        )

    return {"user_id": user["id"], "message": "로그인 성공"}
