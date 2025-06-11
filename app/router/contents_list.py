from fastapi import APIRouter, Depends
from app.core.session import get_current_user
from app.services.contents_list import (
    get_users_contents_list,
    get_users_category_contents_list,
)


router = APIRouter()


@router.get("/contents-list/category/{category_id}")
async def get_category_contents_list(
    category_id: str, user_id: str = Depends(get_current_user)
):
    """
    사용자 카테고리별 게시글 목록 조회 API
    """
    user_id = str(user_id)
    return await get_users_category_contents_list(user_id, category_id)


@router.get("/contents-list")
async def get_contents_list(user_id: str = Depends(get_current_user)):
    """
    사용자 게시글 목록 조회 API
    """
    user_id = str(user_id)
    return await get_users_contents_list(user_id)
