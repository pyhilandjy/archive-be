import subprocess
from app.db.worker import execute_insert_update_query
from app.db.post import INSERT_POST_TITLE, UPDATE_VIDEO_PATH
from supabase import Client, create_client
import os

yt_dlp_path = "/usr/local/bin/yt-dlp"


def download_youtube_video(youtube_url: str, output_file: str):
    """
    yt-dlp로 YouTube 동영상을 mp4 형식으로 다운로드하고 썸네일도 함께 추출합니다.
    """
    try:
        output_base = os.path.splitext(output_file)[0]
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
        return "success"
    except subprocess.CalledProcessError as e:
        print("❌ yt-dlp 실행 실패")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return None


async def upload_to_supabase_and_cleanup(local_file: str):
    """
    Supabase 스토리지에 파일을 업로드하고 스트리밍 URL을 반환합니다.
    """
    try:
        filename = os.path.basename(local_file)
    except Exception as e:
        print(f"예외 발생: {e}")


async def insert_post_to_db(title: str, user_id: str, category_id: str):
    """
    post 테이블에 데이터를 삽입하고 삽입된 ID를 반환합니다.
    """
    params = {
        "title": title,
        "user_id": user_id,
        "category_id": category_id,
    }
    post_id = execute_insert_update_query(INSERT_POST_TITLE, params, return_id=True)
    return str(post_id)


async def update_video_path(post_id: str, video_path: str):
    """
    post 테이블에 비디오 경로를 삽입합니다.
    """
    params = {
        "post_id": post_id,
        "video_path": video_path,
    }
    return execute_insert_update_query(UPDATE_VIDEO_PATH, params, return_id=True)
