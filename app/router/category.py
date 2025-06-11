from fastapi import APIRouter, Depends
from app.core.session import get_current_user
from pydantic import BaseModel
from app.services.category import (
    post_main_category,
    get_categories,
    post_sub_category,
    put_category,
    delete_category,
)

router = APIRouter()


class MainCategoryRequest(BaseModel):
    title: str


@router.post("/main-category")
async def insert_main_category(
    MainCategoryRequest: MainCategoryRequest, user_id: str = Depends(get_current_user)
):
    """
    게시글의 메인 카테고리 등록 API
    """
    user_id = str(user_id)
    return await post_main_category(title=MainCategoryRequest.title, user_id=user_id)


class SubCategoryRequest(BaseModel):
    title: str
    parents_id: str


@router.post("/sub-category")
async def insert_sub_category(
    SubCategoryRequest: SubCategoryRequest, user_id: str = Depends(get_current_user)
):
    """
    게시글의 서브 카테고리 등록 API
    """
    user_id = str(user_id)
    return await post_sub_category(
        SubCategoryRequest.title, SubCategoryRequest.parents_id, user_id
    )


@router.get("/categories")
async def select_categories(user_id: str = Depends(get_current_user)):
    """
    게시글의 메인 카테고리와 서브 카테고리 조회 API
    """
    user_id = str(user_id)
    categories = await get_categories(user_id)
    return categories


class UpdateMainCategoryRequest(BaseModel):
    title: str


@router.put("/category/{id}")
async def update_category(
    id: str,
    UpdateMainCategoryRequest: UpdateMainCategoryRequest,
    user_id: str = Depends(get_current_user),
):
    """
    게시글의 메인 카테고리 수정 API
    """
    user_id = str(user_id)
    await put_category(id=id, title=UpdateMainCategoryRequest.title, user_id=user_id)

    return {"message": "메인 카테고리가 성공적으로 수정되었습니다."}


@router.delete("/category/{id}")
async def remove_category(id: str, user_id: str = Depends(get_current_user)):
    """
    게시글의 메인 카테고리 삭제 API
    """
    user_id = str(user_id)
    await delete_category(id=id, user_id=user_id)
    return {"message": "메인 카테고리가 성공적으로 삭제되었습니다."}
