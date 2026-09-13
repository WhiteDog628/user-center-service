from flask import Blueprint

from app.utils.response import success_response


health_bp = Blueprint(
    "health",
    __name__
)


@health_bp.get("/api/health")
def health_check():
    """
    服务健康检查接口。
    """

    return success_response(
        data={
            "status": "UP"
        }
    )