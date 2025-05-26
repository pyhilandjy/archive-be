from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.signup import user_signup
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str
    user_name: str


@router.post("/signup")
async def signup(request: SignupRequest):
    """
    회원가입 API
    """
    user_id = await user_signup(
        email=request.email, password=request.password, user_name=request.user_name
    )


@router.post("/verify/request")
async def verify_request(email: str):
    """
    이메일 인증 요청 API
    """
