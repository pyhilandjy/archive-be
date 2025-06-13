from app.services.post import (
    download_youtube_video,
    get_storage_paths,
    insert_post_to_db,
    update_video_path,
)
from app.core.session import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class PostRequest(BaseModel):
    title: str
    url: str
    category_id: str


@router.post("/posts")
async def create_post(request: PostRequest, user_id: str = Depends(get_current_user)):
    """
    게시물 업로드 API
    """
    try:
        # Step 1: post 삽입
        post_id = await insert_post_to_db(
            title=request.title,
            user_id=user_id,
            category_id=request.category_id,
        )

        # Step 2: 경로 계산 및 yt-dlp 다운로드
        paths = get_storage_paths(str(user_id), request.category_id, post_id)
        download_success = download_youtube_video(request.url, paths["base"])
        if not download_success:
            raise Exception("영상 다운로드 실패")

        # Step 3: post에 경로 업데이트
        await update_video_path(post_id, paths["video_path"], paths["thumbnail_path"])

        return {
            "post_id": post_id,
            "video_url": paths["video_path"],
            "thumbnail_url": paths["thumbnail_path"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
