from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel
from app.services.login import user_login, test_function
from app.core.session import create_session, get_current_user


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    user = await user_login(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=[{"msg": "이메일 또는 비밀번호가 잘못되었습니다."}],
        )
    user_id = str(user["user_id"])
    await create_session(user_id=user_id, response=response)
    return {"msg": "로그인 성공"}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    test = test_function(user_id)
    if not test:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return {"user_id": user_id}


@router.get("/check-cookie")
async def check_cookie(request: Request):
    session_id = request.cookies.get("session_id")
    return {"session_id": session_id}
