import subprocess
import os
from app.db.worker import execute_insert_update_query
from app.db.post import INSERT_POST_TITLE, UPDATE_VIDEO_PATH

yt_dlp_path = "/usr/local/bin/yt-dlp"
STORAGE_ROOT = "/app/video_storage"


def get_storage_paths(user_id: str, category_id: str, post_id: str) -> dict:
    """
    /video_storage/user_<user_id>/category_<category_id>/<post_id>.mp4
    """
    user_dir = os.path.join(STORAGE_ROOT, f"user_{user_id}", f"category_{category_id}")
    os.makedirs(user_dir, exist_ok=True)

    base_path = os.path.join(user_dir, post_id)
    return {
        "video_path": base_path + ".mp4",
        "thumbnail_path": base_path + ".jpg",
        "base": base_path,
        "url_path": f"/videos/user_{user_id}/category_{category_id}/{post_id}.mp4",
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
    post_id = execute_insert_update_query(INSERT_POST_TITLE, params, return_id=True)
    return str(post_id)


async def update_video_path(post_id: str, video_path: str, thumbnail_path: str):
    try:
        params = {
            "post_id": post_id,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
        }
        execute_insert_update_query(UPDATE_VIDEO_PATH, params)
    except Exception as e:
        print("❌ 비디오 경로 업데이트 실패:", e)
        raise e
