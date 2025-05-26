from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
from app.router import signup

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signup.router, tags=["sign"])


@app.get("/")
def root():
    return {"message": "FastAPI + Redis + JWT 프로젝트 시작"}
