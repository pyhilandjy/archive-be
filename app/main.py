from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.router import category, contents, signup, login, contents_list

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
