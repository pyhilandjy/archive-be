from sqlalchemy import text

INSERT_USER_SIGN = text(
    """
    INSERT INTO users (email, password_hash)
    VALUES (:email, :password_hash)
    RETURNING id;
    """
)

CHECK_EMAIL_EXISTS = text(
    """
    SELECT EXISTS (SELECT 1 FROM users WHERE email = :email);
    """
)

USER_LOGIN_DATA = text(
    """
    SELECT id, password_hash FROM users WHERE email = :email
    """
)


USER_EMAIL = text(
    """
    SELECT email FROM users WHERE id = :user_id
    """
)

UPDATE_USER_PASSWORD = text(
    """
    UPDATE users SET password_hash = :password_hash WHERE email = :email
    """
)
