from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.login import user_login

# from app.auth.jwt import create_access_token
from app.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    """
    로그인 API - 이메일과 비밀번호로 사용자 인증
    """
    try:
        # 사용자 인증
        user = await user_login(email=request.email, password=request.password)
    except HTTPException as e:
        # 인증 실패 시 예외 처리
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    # # JWT 토큰 생성
    # access_token = create_access_token(
    #     data={"user_id": user["user_id"]},
    #     expires_delta=settings.access_token_expire_seconds,
    # )

    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer",
    #     "message": user["message"]
    # }
