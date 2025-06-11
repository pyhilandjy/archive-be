import subprocess
from typing import Optional


yt_dlp_path = "/usr/local/bin/yt-dlp"


async def download_youtube_video(
    youtube_url: str, output_file: str = "downloaded_video.mp4"
) -> Optional[str]:
    """
    yt-dlp로 YouTube 동영상을 mp4 형식으로 다운로드합니다.
    """
    try:
        command = [
            yt_dlp_path,
            "-f",
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "-o",
            output_file,
            youtube_url,
        ]
        subprocess.run(command, check=True)
        print(f"✅ 다운로드 완료: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print("❌ yt-dlp 실행 실패")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return None
