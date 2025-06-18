from app.core.config import settings
from fastapi import HTTPException
from app.db.worker import execute_select_query
from app.db.auth_query import USER_LOGIN_DATA, USER_EMAIL, CHECK_EMAIL_EXISTS
from passlib.context import CryptContext
from app.core.redis import rdb

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

    return {"user_id": user["id"], "msg": "로그인 성공"}


async def select_email(user_id: str):
    """
    테스트용 함수로, 현재 세션 ID를 반환합니다.
    """
    email = execute_select_query(
        USER_EMAIL,
        params={"user_id": user_id},
    )
    return email


async def chenck_email_exists(email: str):
    """
    이메일 중복 확인 함수
    """
    exist = execute_select_query(
        CHECK_EMAIL_EXISTS,
        params={"email": email},
    )
    if not exist:
        raise HTTPException(
            status_code=400, detail=[{"msg": "존재하지 않는 이메일입니다."}]
        )
    return exist


async def reset_password(email: str, new_password: str):
    """
    비밀번호 재설정 함수
    """
    verified = rdb.get(f"verified:{email}")
    if verified != "true":
        raise HTTPException(
            status_code=400, detail=[{"msg": "이메일 인증이 완료되지 않았습니다."}]
        )
    password_hash = pwd_context.hash(new_password)
    execute_select_query(
        "UPDATE users SET password_hash = :password_hash WHERE email = :email",
        params={"password_hash": password_hash, "email": email},
    )
    # 인증 상태 키 삭제 (1회성 보안)
    rdb.delete(f"verified:{email}")
