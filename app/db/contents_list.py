from sqlalchemy import text

GET_CONTENTES_LIST = text(
    """
    select id, title, thumbnail_path
    from contents
    where user_id = :user_id
    order by updated_at desc
    """
)

GET_CATEGORY_CONTENTES_LIST = text(
    """
    select id, title, thumbnail_path
    from contents
    where user_id = :user_id and category_id = :category_id
    order by updated_at desc
    """
)
