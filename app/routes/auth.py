from flask import Blueprint, request

from flask_jwt_extended import create_access_token

from app.services.user_service import (
    create_user,
    email_exists,
    username_exists
)

from app.models import User

from app.utils.response import (
    error_response,
    success_response
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth"
)


@auth_bp.post("/register")
def register():
    """
    用户注册接口。
    """

    data = request.get_json()

    if not data:
        return error_response(
            message="request body is empty"
        )

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")


    if not username:
        return error_response(
            message="username is required"
        )

    if not email:
        return error_response(
            message="email is required"
        )

    if not password:
        return error_response(
            message="password is required"
        )


    if username_exists(username):
        return error_response(
            message="username already exists",
            code=1001,
            status_code=409
        )


    if email_exists(email):
        return error_response(
            message="email already exists",
            code=1002,
            status_code=409
        )


    user = create_user(
        username=username,
        email=email,
        password=password
    )


    return success_response(
        data=user.to_dict(),
        message="register success"
    )


@auth_bp.post("/login")
def login():
    """
    用户登录接口。

    流程：
    1. 获取用户名和密码；
    2. 查询用户；
    3. 校验密码；
    4. 生成 JWT Token。
    """

    data = request.get_json()


    if not data:
        return error_response(
            message="request body is empty"
        )


    username = data.get("username")
    password = data.get("password")


    if not username:
        return error_response(
            message="username is required"
        )


    if not password:
        return error_response(
            message="password is required"
        )


    # 查询用户
    user = (
        User.query
        .filter_by(username=username)
        .first()
    )


    if not user:
        return error_response(
            message="user not found",
            code=2001,
            status_code=401
        )


    # 校验密码
    if not user.check_password(password):
        return error_response(
            message="password incorrect",
            code=2002,
            status_code=401
        )


    # 创建JWT Token
    access_token = create_access_token(
        identity=str(user.id)
    )


    return success_response(
        data={
            "access_token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict()
        },
        message="login success"
    )