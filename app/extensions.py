from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


# SQLAlchemy 数据库扩展对象
db = SQLAlchemy()

# JWT 鉴权扩展对象
jwt = JWTManager()