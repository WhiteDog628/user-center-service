from app.extensions import db
from app.models import User


def create_user(
    username,
    email,
    password
):
    """
    创建用户。

    返回:
        User对象
    """

    user = User(
        username=username,
        email=email
    )

    # 密码哈希处理
    user.set_password(password)

    db.session.add(user)

    db.session.commit()

    return user


def username_exists(username):
    """
    判断用户名是否存在。
    """

    return (
        User.query
        .filter_by(username=username)
        .first()
        is not None
    )


def email_exists(email):
    """
    判断邮箱是否存在。
    """

    return (
        User.query
        .filter_by(email=email)
        .first()
        is not None
    )