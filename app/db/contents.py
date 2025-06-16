from sqlalchemy import text

INSERT_POST_TITLE = text(
    """
    INSERT INTO contents (title, user_id, category_id)
    VALUES (:title, :user_id, :category_id)
    RETURNING id;
    """
)


UPDATE_VIDEO_PATH = text(
    """
    UPDATE contents
    SET video_path = :video_path, thumbnail_path = :thumbnail_path
    WHERE id = :contents_id;
    """
)

SELECT_CONTENTS_BY_ID = text(
    """
    SELECT title, video_path, thumbnail_path, description FROM contents
    WHERE id = :contents_id;
    """
)
UPDATE_CONTENTS_DESCRIPTION = text(
    """
    UPDATE contents 
    SET description = :description 
    WHERE id = :contents_id
    """
)

DELETE_CONTENTS = text(
    """
    DELETE FROM contents 
    WHERE id = :contents_id
    """
)
