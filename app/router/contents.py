from app.services.contents import (
    get_storage_paths,
    insert_post_to_db,
    update_video_path,
    get_contents_by_id,
    update_contents_description,
    delete_contents,
    get_category_id_contents_by_id,
    download_queue,
    fetch_all_titles_and_urls_from_playlist,
    remove_queryparams_youtube_url,
)
from app.core.session import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class PostRequest(BaseModel):
    title: Optional[str] = None
    url: str
    category_id: str
    is_list: bool


class UpdateDescriptionRequest(BaseModel):
    description: str


@router.get("/contents/{contents_id}/category_id")
async def get_category_id(contents_id: str, user_id: str = Depends(get_current_user)):
    """
    게시글 ID로 카테고리 ID 조회 API
    """
    try:
        category_id = await get_category_id_contents_by_id(contents_id, user_id)
        return category_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contents/{contents_id}")
async def get_post(contents_id: str, user_id: str = Depends(get_current_user)):
    """
    게시물 조회 API(title, description, video_path, thumbnail_path)
    """
    try:
        contents = await get_contents_by_id(contents_id, user_id)
        return contents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contents/{contents_id}/description")
async def update_post_description(
    contents_id: str,
    request: UpdateDescriptionRequest,
    user_id: str = Depends(get_current_user),
):
    """
    게시물 설명 업데이트 API
    """
    try:
        await update_contents_description(contents_id, request.description, user_id)
        return {"message": "게시물 설명이 성공적으로 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contents")
async def create_post(request: PostRequest, user_id: str = Depends(get_current_user)):
    contents_id = None
    try:
        if request.is_list:
            videos = await fetch_all_titles_and_urls_from_playlist(request.url)
        else:
            clean_url = await remove_queryparams_youtube_url(request.url)
            videos = [{"title": request.title, "url": clean_url}]
        print(f"📥 비디오 목록: {videos}")
        for video in videos:
            vid_title = video["title"] or video.get("title", "")
            vid_id = await insert_post_to_db(
                title=vid_title,
                user_id=user_id,
                category_id=request.category_id,
            )
            paths = await get_storage_paths(str(user_id), request.category_id, vid_id)
            await update_video_path(
                vid_id, paths["video_path"], paths["thumbnail_path"]
            )
            await download_queue.put(
                {
                    "contents_id": vid_id,
                    "youtube_url": video["url"],
                    "output_base": paths["base"],
                    "user_id": str(user_id),
                }
            )

        return {"contents_id": contents_id}

    except Exception as e:
        if contents_id:
            await delete_contents(contents_id, user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contents/{contents_id}")
async def delete_post(contents_id: str, user_id: str = Depends(get_current_user)):
    """
    게시물 삭제 API
    """
    try:
        # Step 1: 게시글 삭제
        await delete_contents(contents_id, user_id)  # category_id는 None으로 설정
        return {"message": "게시물이 성공적으로 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/youtube-playlist")
async def get_youtube_playlist(playlist_url: str):
    """
    유튜브 플레이리스트에서 비디오 목록을 가져오는 API
    """
    return await remove_queryparams_youtube_url(playlist_url)
