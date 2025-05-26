from sqlalchemy import text

INSERT_USER_SIGN = text(
    """
    INSERT INTO users (email, password_hash, user_name)
    VALUES (:email, :password_hash, :user_name)
    RETURNING id;
    """
)

CHECK_EMAIL_EXISTS = text(
    """
    SELECT EXISTS (SELECT 1 FROM users WHERE email = :email);
    """
)
