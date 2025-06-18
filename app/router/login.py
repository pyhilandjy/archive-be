from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel
from app.services.login import (
    user_login,
    select_email,
    chenck_email_exists,
    reset_password,
)
from app.core.session import create_session, get_current_user
from app.core.redis import rdb


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    user = await user_login(request.email, request.password)
    user_id = str(user["user_id"])
    await create_session(user_id=user_id, response=response)
    return {"msg": "로그인 성공"}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user_id = str(user_id)
    email = await select_email(user_id)
    if not email:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return email


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await rdb.delete(session_id)

        response.delete_cookie(
            key="session_id",
            samesite="None",
            secure=True,
        )

    return {"msg": "logged out"}


@router.get("/email-exists/{email}")
async def email_exists(email: str):
    """
    이메일 존재 여부 확인 API
    """
    return await chenck_email_exists(email)


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


@router.post("/reset-password")
async def reset_password_endpoint(ResetPasswordRequest: ResetPasswordRequest):
    """
    비밀번호 재설정 API
    """
    await reset_password(ResetPasswordRequest.email, ResetPasswordRequest.new_password)
    return {"msg": "비밀번호가 성공적으로 재설정되었습니다."}
