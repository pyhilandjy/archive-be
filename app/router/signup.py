from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.services.signup import user_signup, user_verify_request, user_verify
import redis
import re
from fastapi.responses import JSONResponse

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(request: SignupRequest):
    """
    회원가입 API
    """
    # 비밀번호 조건 검사
    if not re.match(r"^(?=.*[a-z])(?=.*\d).{8,}$", request.password):
        raise HTTPException(
            status_code=422,
            detail="비밀번호 조건에 충족하지 못했습니다.",
        )
    await user_signup(email=request.email, password=request.password)
    return JSONResponse(content={"success": True})  # 성공 여부 반환


class VerifyRequest(BaseModel):
    email: EmailStr


@router.post("/verify/request")
async def verify_request(request: VerifyRequest):
    """
    이메일 인증 요청 API
    """
    await user_verify_request(email=request.email)
    return JSONResponse(content={"success": True})  # 성공 여부 반환


class VerifyConfirmRequest(BaseModel):
    email: str
    otp: str


@router.post("/verify/confirm")
async def verify_confirm(request: VerifyConfirmRequest):
    """
    이메일 인증 확인 API
    """
    await user_verify(email=request.email, otp=request.otp)
    return JSONResponse(content={"success": True})  # 성공 여부 반환
