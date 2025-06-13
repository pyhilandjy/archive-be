from sqlalchemy import text

INSERT_POST_TITLE = text(
    """
    INSERT INTO post (title, user_id, category_id)
    VALUES (:title, :user_id, :category_id)
    RETURNING id;
    """
)


UPDATE_VIDEO_PATH = text(
    """
    UPDATE post
    SET video_path = :video_path
    WHERE id = :post_id;
    """
)
