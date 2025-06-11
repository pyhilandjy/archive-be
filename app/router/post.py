from app.services.youtube_downloader import download_youtube_video
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class YouTubeDownloadRequest(BaseModel):
    url: str


@router.post("/youtube/download")
async def youtube_download(request: YouTubeDownloadRequest):
    """
    YouTube 동영상 다운로드 API
    """
    output_file = "output.mp4"
    try:
        await download_youtube_video(request.url, output_file)
        return {"message": "다운로드가 완료되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
