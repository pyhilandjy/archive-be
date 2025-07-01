from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.services.websocket_manager import websocket_manager
from fastapi.staticfiles import StaticFiles
from app.router import (
    category,
    contents,
    signup,
    login,
    contents_list,
)
from app.services.contents import download_worker
import asyncio


async def lifespan(app: FastAPI):
    """
    앱 시작 시 다운로드 워커 실행
    """
    for _ in range(3):
        asyncio.create_task(download_worker())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://youtube-study-archive.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/videos", StaticFiles(directory="/app/video_storage"), name="videos")

app.include_router(signup.router, tags=["sign"])
app.include_router(login.router, tags=["login"])
app.include_router(category.router, tags=["category"])
app.include_router(contents_list.router, tags=["contents_list"])
app.include_router(contents.router, tags=["contents"])


@app.get("/")
def root():
    return {"message": "FastAPI + Redis + JWT 프로젝트 시작"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    websocket_manager.register(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.remove(user_id)
