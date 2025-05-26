import random
import redis
from fastapi import HTTPException
from passlib.context import CryptContext
from app.db.worker import execute_insert_update_query, execute_select_query
from app.db.query import INSERT_USER_SIGN, CHECK_EMAIL_EXISTS
from email.message import EmailMessage
import aiosmtplib
import os
from app.config import settings


# Redis 연결
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# 비밀번호 해시 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def send_email_otp(email: str, otp: str):
    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = email
    message["Subject"] = "인증 코드 안내"
    message.set_content(
        f"인증 코드는 다음과 같습니다:\n\n{otp}\n\n5분 안에 입력해주세요."
    )
    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=settings.smtp_user,
        password=settings.smtp_password,
    )


def generate_otp(length: int = 6) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


async def user_signup(email: str, password: str, user_name: str):
    """
    회원가입 API - 이메일 인증된 사용자만 가입 가능
    """
    verified = r.get(f"verified:{email}")
    if verified != "true":
        raise HTTPException(
            status_code=400, detail="이메일 인증이 완료되지 않았습니다."
        )

    password_hash = pwd_context.hash(password)

    try:
        user_id = execute_insert_update_query(
            INSERT_USER_SIGN,
            params={
                "email": email,
                "password_hash": password_hash,
                "user_name": user_name,
            },
            return_id=True,
        )

        # 인증 상태 키 삭제 (1회성 보안)
        r.delete(f"verified:{email}")
        return {"user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def user_verify_request(email: str):
    """
    이메일 인증 요청 API - OTP 생성 + Redis 저장 + 이메일 발송
    """

    if await execute_select_query(query=CHECK_EMAIL_EXISTS, params={"email": email}):
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    if r.get(f"otp_cooldown:{email}"):
        raise HTTPException(status_code=429, detail="잠시 후 다시 시도해주세요.")

    otp = generate_otp()

    r.setex(f"otp:{email}", 300, otp)  # 5분 유효
    r.setex(f"otp_cooldown:{email}", 30, "1")  # 30초 쿨다운

    # 이메일 전송
    await send_email_otp(email, otp)


async def user_verify(email: str, otp: str):
    """
    이메일 인증 검증 API - 사용자가 입력한 OTP가 일치하는지 확인
    """

    stored_otp = r.get(f"otp:{email}")
    if not stored_otp:
        raise HTTPException(
            status_code=400, detail="OTP가 존재하지 않거나 만료되었습니다."
        )

    if stored_otp != otp:
        raise HTTPException(status_code=400, detail="OTP가 올바르지 않습니다.")

    # 검증 성공 처리
    r.delete(f"otp:{email}")  # OTP 재사용 방지
    r.setex(f"verified:{email}", 600, "true")  # 가입 가능 상태 표시 (10분 유효)

    return {"message": "이메일 인증이 완료되었습니다."}
