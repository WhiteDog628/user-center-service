from flask import Blueprint

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)

from app.utils.response import success_response


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/api/v1/users"
)


@user_bp.get("/me")
@jwt_required()
def get_current_user():
    """
    获取当前登录用户信息。

    需要携带 JWT Token。
    """

    user_id = get_jwt_identity()

    return success_response(
        data={
            "user_id": user_id
        },
        message="get current user success"
    )