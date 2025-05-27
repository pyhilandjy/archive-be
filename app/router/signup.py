from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.signup import user_signup, user_verify_request, user_verify
import redis

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
    await user_signup(email=request.email, password=request.password)


@router.post("/verify/request")
async def verify_request(email: str):
    """
    이메일 인증 요청 API
    """
    await user_verify_request(email=email)


@router.post("/verify/confirm")
async def verify_confirm(email: str, otp: str):
    """
    이메일 인증 확인 API
    """
    return await user_verify(email=email, otp=otp)
