import os

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig


@pytest.fixture(scope="session")
def base_url():
    """
    HTTP 集成测试的服务基础地址。

    默认访问独立测试服务：
    http://127.0.0.1:5001

    如需测试其他环境，可以通过
    BASE_URL 环境变量覆盖默认地址。
    """

    return os.getenv(
        "BASE_URL",
        "http://127.0.0.1:5001"
    )


@pytest.fixture(
    scope="session",
    autouse=True
)
def clean_integration_test_data():
    """
    HTTP 集成测试数据清理。

    测试开始前：
        清空测试数据库中的 users 数据。

    测试结束后：
        再次清空 users 数据。

    只清理数据，不删除表结构，
    避免影响正在运行的 Test Server。
    """

    test_app = create_app(TestConfig)

    # 测试开始前清理历史数据
    with test_app.app_context():
        db.session.query(User).delete()
        db.session.commit()

    yield

    # 整个测试会话结束后再次清理
    with test_app.app_context():
        db.session.query(User).delete()
        db.session.commit()
        db.session.remove()