import random
from fastapi import HTTPException
from passlib.context import CryptContext
from app.db.worker import execute_insert_update_query, execute_select_query
from app.db.auth_query import INSERT_USER_SIGN, CHECK_EMAIL_EXISTS
from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings
from app.core.redis import rdb

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


async def user_signup(email: str, password: str):
    """
    회원가입 API - 이메일 인증된 사용자만 가입 가능
    """
    verified = await rdb.get(f"verified:{email}")
    if verified != "true":
        raise HTTPException(
            status_code=400, detail=[{"msg": "이메일 인증이 완료되지 않았습니다."}]
        )

    password_hash = pwd_context.hash(password)

    try:
        user_id = execute_insert_update_query(
            INSERT_USER_SIGN,
            params={
                "email": email,
                "password_hash": password_hash,
            },
            return_id=True,
        )

        # 인증 상태 키 삭제 (1회성 보안)
        await rdb.delete(f"verified:{email}")
        return {"user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def user_verify_request(email: str, mode: str):
    """
    이메일 인증 요청 API - OTP 생성 + Redis 저장 + 이메일 발송
    """
    if mode == "signup":
        is_exist = execute_select_query(
            query=CHECK_EMAIL_EXISTS, params={"email": email}
        )
        if is_exist[0]["exists"]:
            raise HTTPException(
                status_code=409, detail=[{"msg": "이미 가입된 이메일입니다."}]
            )
        if await rdb.get(f"otp_cooldown:{email}"):
            raise HTTPException(
                status_code=429, detail=[{"msg": "잠시 후 다시 시도해주세요."}]
            )
    elif mode == "reset_password":
        pass
    otp = generate_otp()

    await rdb.setex(f"otp:{email}", 300, otp)  # 5분 유효
    await rdb.setex(f"otp_cooldown:{email}", 10, "1")  # 30초 쿨다운

    # 이메일 전송
    await send_email_otp(email, otp)


async def user_verify(email: str, otp: str):
    """
    이메일 인증 검증 API - 사용자가 입력한 OTP가 일치하는지 확인
    """

    stored_otp = await rdb.get(f"otp:{email}")
    if not stored_otp:
        raise HTTPException(
            status_code=400, detail=[{"msg": "OTP가 존재하지 않거나 만료되었습니다."}]
        )

    if stored_otp != otp:
        raise HTTPException(
            status_code=400, detail=[{"msg": "OTP가 올바르지 않습니다."}]
        )

    # 검증 성공 처리
    await rdb.delete(f"otp:{email}")  # OTP 재사용 방지
    await rdb.setex(f"verified:{email}", 600, "true")  # 가입 가능 상태 표시 (10분 유효)

    return {"message": "이메일 인증이 완료되었습니다."}
