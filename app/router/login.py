from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel
from app.services.login import user_login, test_function
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
    email = await test_function(user_id)
    if not email:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return email


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await rdb.delete(session_id)
        response.delete_cookie("session_id")
    return {"message": "logged out"}
