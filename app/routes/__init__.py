from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.user import user_bp


__all__ = [
    "health_bp",
    "auth_bp",
    "user_bp"
]