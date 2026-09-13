import os
from datetime import timedelta

from dotenv import load_dotenv


# 加载项目根目录中的 .env 文件
load_dotenv()


class Config:
    """
    Flask 项目的基础配置类。

    数据库地址、JWT 密钥等配置统一从环境变量读取，
    避免将敏感信息直接硬编码到业务代码中。
    """

    # 开发环境 MySQL 数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 签名密钥
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "default-development-secret"
    )

    # Access Token 有效时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(
            os.getenv(
                "JWT_ACCESS_TOKEN_MINUTES",
                "30"
            )
        )
    )

    JSON_SORT_KEYS = False


class TestConfig(Config):
    """
    pytest 自动化测试环境配置。

    使用独立测试数据库，
    避免测试数据污染开发数据库。
    """

    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL"
    )