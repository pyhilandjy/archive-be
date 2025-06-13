from app.services.post import (
    download_youtube_video,
    upload_to_supabase_and_cleanup,
    insert_post_to_db,
    update_video_path,
)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class PostRequest(BaseModel):
    title: str
    url: str
    user_id: str
    category_id: str


@router.post("/posts")
async def create_post(request: PostRequest):
    """
    게시물 업로드 API
    """
    try:
        # title, user_id, category_id를 사용하여 post 테이블에 데이터 삽입
        post_id = await insert_post_to_db(
            title=request.title,
            user_id=request.user_id,
            category_id=request.category_id,
        )

        # YouTube 동영상 다운로드
        output_file = f"{post_id}.mp4"
        await download_youtube_video(request.url, output_file)

        # Supabase 스토리지 업로드 및 스트리밍 URL 생성
        streaming_url = await upload_to_supabase_and_cleanup(output_file)

        # post 테이블에 streaming_url 삽입
        update_video_path(post_id, streaming_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
