import subprocess
import os
from app.core.config import settings
from app.db.worker import execute_insert_update_query
from app.db.post import INSERT_POST_TITLE, UPDATE_VIDEO_PATH

yt_dlp_path = "/usr/local/bin/yt-dlp"
STORAGE_ROOT = "/app/video_storage"
be_url = settings.be_url


def get_storage_paths(user_id: str, category_id: str, contents_id: str) -> dict:
    user_dir = os.path.join(STORAGE_ROOT, f"user_{user_id}", f"category_{category_id}")
    os.makedirs(user_dir, exist_ok=True)

    filename = f"{contents_id}"
    base_path = os.path.join(user_dir, filename)

    return {
        "video_path": f"{be_url}/videos/user_{user_id}/category_{category_id}/{filename}.mp4",
        "thumbnail_path": f"{be_url}/videos/user_{user_id}/category_{category_id}/{filename}.jpg",
        "base": base_path,
    }


def download_youtube_video(youtube_url: str, output_base: str) -> bool:
    try:
        command = [
            yt_dlp_path,
            "-f",
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "--write-thumbnail",
            "--convert-thumbnails",
            "jpg",
            "-o",
            output_base + ".%(ext)s",
            youtube_url,
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ yt-dlp 실행 실패")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return False


async def insert_post_to_db(title: str, user_id: str, category_id: str) -> str:
    params = {
        "title": title,
        "user_id": user_id,
        "category_id": category_id,
    }
    contents_id = execute_insert_update_query(INSERT_POST_TITLE, params, return_id=True)
    return str(contents_id)


async def update_video_path(contents_id: str, video_path: str, thumbnail_path: str):
    try:
        params = {
            "contents_id": contents_id,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
        }
        execute_insert_update_query(UPDATE_VIDEO_PATH, params)
    except Exception as e:
        print("❌ 비디오 경로 업데이트 실패:", e)
        raise e
