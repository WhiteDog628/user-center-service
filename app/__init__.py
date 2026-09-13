from flask import Flask

from app.extensions import db, jwt
from app.routes import auth_bp, health_bp, user_bp
from config import Config


def create_app(config_class=Config):
    """
    Flask Application Factory。

    负责完成 Flask 应用的基础组装：
    1. 创建 Flask 应用实例；
    2. 加载项目配置；
    3. 初始化 SQLAlchemy；
    4. 初始化 JWT；
    5. 注册 Blueprint 路由。

    参数：
        config_class:
            Flask 配置类，默认使用项目中的 Config。
            后续测试环境可以传入独立的 TestConfig。
    """

    app = Flask(__name__)

    # 加载 Flask 配置
    app.config.from_object(config_class)

    # 将 SQLAlchemy 与当前 Flask 应用绑定
    db.init_app(app)

    # 将 JWTManager 与当前 Flask 应用绑定
    jwt.init_app(app)

    # 注册健康检查 Blueprint
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    return app