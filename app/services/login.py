from app.core.config import settings
from fastapi import HTTPException
from app.db.worker import execute_select_query
from app.db.auth_query import USER_LOGIN_DATA, USER_EMAIL
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
            status_code=401, detail=[{"msg": "존재하지 않는 이메일입니다."}]
        )

    user = user[0]
    if not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(
            status_code=401, detail=[{"msg": "비밀번호가 잘못되었습니다."}]
        )

    return {"user_id": user["id"], "message": "로그인 성공"}


async def test_function(user_id: str):
    """
    테스트용 함수로, 현재 세션 ID를 반환합니다.
    """
    email = execute_select_query(
        USER_EMAIL,
        params={"user_id": user_id},
    )
    return email
