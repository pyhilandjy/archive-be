from fastapi import HTTPException
from app.db.worker import execute_select_query, execute_insert_update_query
from app.db.category_query import (
    POST_MAIN_CATEGORY,
    GET_CATEGORIES,
    POST_SUB_CATEGORY,
    UPDATE_CATEGORY,
    DELETE_CATEGORY,
    GET_CATEGORIY_BY_ID,
)
import os
import shutil


async def post_main_category(title: str, user_id: str):
    """
    게시글의 메인 카테고리 조회
    """
    # 게시글의 메인 카테고리 조회 로직
    try:
        id = execute_insert_update_query(
            query=POST_MAIN_CATEGORY,
            params={"title": title, "user_id": user_id},
            return_id=True,
        )
        return await get_categoriy_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_categoriy_by_id(id):
    """
    게시글의 메인 카테고리와 서브 카테고리 조회
    """
    try:
        categories = execute_select_query(query=GET_CATEGORIY_BY_ID, params={"id": id})
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def post_sub_category(title: str, parents_id: str, user_id: str):
    """
    게시글의 서브 카테고리 등록
    """
    # 게시글의 서브 카테고리 등록 로직
    try:
        execute_insert_update_query(
            query=POST_SUB_CATEGORY,
            params={"title": title, "parents_id": parents_id, "user_id": user_id},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "서브 카테고리가 성공적으로 등록되었습니다."}


async def get_categories(user_id):
    """
    게시글의 메인 카테고리와 서브 카테고리 조회
    """
    try:
        categories = execute_select_query(
            query=GET_CATEGORIES, params={"user_id": user_id}
        )
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def put_category(id: str, title: str, user_id: str):
    """
    게시글의 메인 카테고리 수정
    """
    try:
        execute_insert_update_query(
            query=UPDATE_CATEGORY,
            params={"id": id, "title": title, "user_id": user_id},
        )
        return {"message": "메인 카테고리가 성공적으로 수정되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def delete_category(id: str, user_id: str):
    """
    게시글의 메인 카테고리 삭제
    """
    try:
        # Step 1: 데이터베이스에서 카테고리 삭제
        execute_insert_update_query(
            query=DELETE_CATEGORY,
            params={"id": id, "user_id": user_id},
        )

        # Step 2: 파일 시스템에서 관련 디렉토리 삭제
        category_dir = os.path.join(
            "/app/video_storage", f"user_{user_id}", f"category_{id}"
        )
        if os.path.exists(category_dir):
            shutil.rmtree(category_dir)

        return {"message": "메인 카테고리가 성공적으로 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
