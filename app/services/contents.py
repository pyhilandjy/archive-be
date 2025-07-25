import os
import json
import shutil
import asyncio
from uuid import uuid4
from app.services.websocket_manager import websocket_manager
from app.core.config import settings
from app.db.worker import execute_insert_update_query, execute_select_query
from app.db.contents import (
    INSERT_POST_TITLE,
    UPDATE_VIDEO_PATH,
    SELECT_CONTENTS_BY_ID,
    UPDATE_CONTENTS_DESCRIPTION,
    DELETE_CONTENTS,
    SELECT_CONTENTS_CATEGORY_BY_ID,
    UPDATE_CONTENTS_STATUS,
)

yt_dlp_path = "/usr/local/bin/yt-dlp"
STORAGE_ROOT = "/app/video_storage"
be_url = settings.be_url


async def get_storage_paths(user_id: str, category_id: str, contents_id: str) -> dict:
    user_dir = os.path.join(STORAGE_ROOT, f"user_{user_id}", f"category_{category_id}")
    os.makedirs(user_dir, exist_ok=True)

    filename = f"{contents_id}"
    base_path = os.path.join(user_dir, filename)

    return {
        "video_path": f"/videos/user_{user_id}/category_{category_id}/{filename}.mp4",
        "thumbnail_path": f"/videos/user_{user_id}/category_{category_id}/{filename}.jpg",
        "base": base_path,
    }


async def download_youtube_video(youtube_url: str, output_base: str) -> bool:
    """
    유튜브 다운로드
    """
    command = [
        yt_dlp_path,
        "-f",
        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "--write-thumbnail",
        "--convert-thumbnails",
        "jpg",
        "--concurrent-fragments",
        "8",
        "--retries",
        "3",
        "--fragment-retries",
        "3",
        "-o",
        output_base + ".%(ext)s",
        youtube_url,
    ]

    try:
        # asyncio subprocess 사용 (I/O 바운드 최적화)
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print("stdout:", stdout.decode())
            print(f"다운로드 성공: {youtube_url}")
            return True
        else:
            print(f"다운로드 실패 - stderr: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"다운로드 오류: {str(e)}")
        print(f"❌ 다운로드 실패: {youtube_url}")
        return False


async def delete_contents_metadata(contents_id: str, user_id: str):
    """
    게시글 메타데이터 삭제
    """
    try:
        params = {"contents_id": contents_id, "user_id": user_id}
        execute_insert_update_query(query=DELETE_CONTENTS, params=params)
    except Exception as e:
        print("❌ 게시글 메타데이터 삭제 실패:", e)
        raise e


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


async def get_contents_by_id(contents_id: str, user_id: str):
    """
    게시글 ID로 게시글 조회
    """
    try:
        contents = execute_select_query(
            query=SELECT_CONTENTS_BY_ID,
            params={"contents_id": contents_id, "user_id": user_id},
        )
        updated_contents = []
        for item in contents:
            item = dict(item)
            if "thumbnail_path" in item:
                item["thumbnail_path"] = settings.be_url + item["thumbnail_path"]
            if "video_path" in item:
                item["video_path"] = settings.be_url + item["video_path"]
            updated_contents.append(item)

        return updated_contents
    except Exception as e:
        raise e


async def update_contents_description(contents_id: str, description: str, user_id: str):
    """
    게시글 설명 업데이트
    """
    try:
        params = {
            "contents_id": contents_id,
            "description": description,
            "user_id": user_id,
        }
        execute_insert_update_query(query=UPDATE_CONTENTS_DESCRIPTION, params=params)
    except Exception as e:
        print("❌ 게시글 설명 업데이트 실패:", e)
        raise e


async def delete_contents(contents_id: str, user_id: str):
    """
    게시글 삭제
    """
    try:
        user_id = str(user_id)
        category_id = await get_category_id_contents_by_id(contents_id, user_id)
        category_id = category_id.get("category_id")
        # Step 1: 데이터베이스에서 게시글 삭제
        execute_insert_update_query(
            query=DELETE_CONTENTS,
            params={"contents_id": contents_id, "user_id": user_id},
        )

        # Step 2: 파일 시스템에서 관련 파일 삭제
        storage_paths = await get_storage_paths(user_id, category_id, contents_id)
        base_path = storage_paths["base"]

        # 삭제 대상 파일들
        video_file = base_path + ".mp4"
        thumbnail_file = base_path + ".jpg"

        # 파일 삭제
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)

        # 디렉토리 정리 (필요 시)
        user_dir = os.path.dirname(base_path)
        if os.path.exists(user_dir) and not os.listdir(user_dir):
            shutil.rmtree(user_dir)

    except Exception as e:
        print("❌ 게시글 삭제 실패:", e)
        raise e


async def get_category_id_contents_by_id(contents_id: str, user_id: str):
    """
    게시글 ID로 카테고리 ID 조회
    """
    try:
        result = execute_select_query(
            query=SELECT_CONTENTS_CATEGORY_BY_ID,
            params={"contents_id": contents_id, "user_id": user_id},
        )
        row = result[0]
        return {"category_id": str(row["category_id"])}
    except Exception as e:
        print("❌ 게시글 조회 실패:", e)
        raise e


# 다운로드 작업 큐 정의
download_queue: asyncio.Queue = asyncio.Queue()


async def download_worker():
    while True:
        task = await download_queue.get()
        contents_id = task["contents_id"]
        youtube_url = task["youtube_url"]
        output_base = task["output_base"]
        user_id = task["user_id"]

        try:
            await update_download_status(contents_id, "ON_PROCESS")
            await websocket_manager.send(
                user_id,
                {
                    "type": "status_update",
                    "contents_id": contents_id,
                    "status": "ON_PROCESS",
                },
            )

            success = await download_youtube_video(youtube_url, output_base)

            new_status = "DONE" if success else "FAILED"
            await update_download_status(contents_id, new_status)
            await websocket_manager.send(
                user_id,
                {
                    "type": "status_update",
                    "contents_id": contents_id,
                    "status": new_status,
                },
            )

        except Exception as e:
            await update_download_status(contents_id, "FAILED")
            await websocket_manager.send(
                user_id,
                {
                    "type": "status_update",
                    "contents_id": contents_id,
                    "status": "FAILED",
                    "error": str(e),
                },
            )

        finally:
            download_queue.task_done()


async def update_download_status(contents_id: str, status: str):
    """
    다운로드 상태를 업데이트
    """
    params = {"contents_id": contents_id, "status": status}
    execute_insert_update_query(query=UPDATE_CONTENTS_STATUS, params=params)


async def fetch_all_titles_and_urls_from_playlist(playlist_url: str) -> list[dict]:
    """
    유튜브 플레이리스트나 자동 재생 리스트에서 모든 영상의 {title, url} 목록 추출
    """
    try:
        command = [
            yt_dlp_path,
            "--flat-playlist",
            "--print-json",
            "--no-warnings",
            playlist_url,
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"yt-dlp 오류: {stderr.decode().strip()}")

        # 출력된 JSON 라인별 파싱
        items = []
        for line in stdout.decode().strip().splitlines():
            info = json.loads(line)
            if "title" in info and "id" in info:
                items.append(
                    {
                        "title": info["title"],
                        "url": f"https://www.youtube.com/watch?v={info['id']}",
                    }
                )

        return items

    except Exception as e:
        print(f"❌ 플레이리스트 영상 정보 추출 실패: {str(e)}")
        raise e


async def remove_queryparams_youtube_url(url):
    return url.split("&", 1)[0]
