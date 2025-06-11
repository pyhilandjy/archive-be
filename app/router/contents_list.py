from fastapi import APIRouter, Depends
from app.core.session import get_current_user
from pydantic import BaseModel


router = APIRouter()
