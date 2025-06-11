from fastapi import HTTPException
from app.db.worker import execute_select_query
from app.db.contents_list import GET_CONTENTES_LIST


async def get_users_contents_list(user_id: str):
    """
    사용자 게시글 목록 조회
    """
    try:
        contents = execute_select_query(
            query=GET_CONTENTES_LIST,
            params={"user_id": user_id},
        )

        contents = contents * 30  # 스크롤 테스트용
        return contents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_users_category_contents_list(user_id: str, category_id: str):
    """
    사용자 카테고리별 게시글 목록 조회
    """
    try:
        contents = execute_select_query(
            query=GET_CONTENTES_LIST,
            params={"user_id": user_id, "category_id": category_id},
        )
        return contents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
