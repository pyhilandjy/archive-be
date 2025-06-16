from app.services.contents import (
    download_youtube_video,
    get_storage_paths,
    insert_post_to_db,
    update_video_path,
    get_contents_by_id,
    update_contents_description,
    delete_contents,
    get_category_id_contents_by_id,
)
from app.core.session import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class PostRequest(BaseModel):
    title: str
    url: str
    category_id: str


class UpdateDescriptionRequest(BaseModel):
    description: str


@router.get("/contents/{contents_id}/category_id")
async def get_category_id(contents_id: str):
    """
    게시글 ID로 카테고리 ID 조회 API
    """
    try:
        category_id = await get_category_id_contents_by_id(contents_id)
        return category_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contents/{contents_id}")
async def get_post(contents_id: str):
    """
    게시물 조회 API(title, description, video_path, thumbnail_path)
    """
    try:
        contents = await get_contents_by_id(contents_id)
        return contents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contents/{contents_id}/description")
async def update_post_description(contents_id: str, request: UpdateDescriptionRequest):
    """
    게시물 설명 업데이트 API
    """
    try:
        await update_contents_description(contents_id, request.description)
        return {"message": "게시물 설명이 성공적으로 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contents")
async def create_post(request: PostRequest, user_id: str = Depends(get_current_user)):
    """
    게시물 업로드 API
    """
    try:
        # Step 1: post 삽입
        contents_id = await insert_post_to_db(
            title=request.title,
            user_id=user_id,
            category_id=request.category_id,
        )

        # Step 2: 경로 계산 및 yt-dlp 다운로드
        paths = get_storage_paths(str(user_id), request.category_id, contents_id)
        download_success = download_youtube_video(request.url, paths["base"])
        if not download_success:
            raise Exception("영상 다운로드 실패")

        # Step 3: post에 경로 업데이트
        await update_video_path(
            contents_id, paths["video_path"], paths["thumbnail_path"]
        )

        return {
            "contents_id": contents_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contents/{contents_id}")
async def delete_post(
    contents_id: str, category_id: str, user_id: str = Depends(get_current_user)
):
    """
    게시물 삭제 API
    """
    try:
        # Step 1: 게시글 삭제
        await delete_contents(
            contents_id, user_id, category_id
        )  # category_id는 None으로 설정
        return {"message": "게시물이 성공적으로 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
