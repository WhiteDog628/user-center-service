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
    HTTP 集成测试数据库初始化与数据清理。

    测试开始前：
        1. 确保测试数据库表结构存在；
        2. 清空 users 表中的历史测试数据。

    测试结束后：
        再次清空 users 表中的测试数据。

    保留表结构，避免影响正在运行的 Test Server。
    """

    test_app = create_app(TestConfig)

    with test_app.app_context():
        # 确保测试库表结构存在。
        # 即使此前其他测试执行了 db.drop_all()，
        # 集成测试也能够自行恢复所需表结构。
        db.create_all()

        # 清理历史测试数据
        db.session.query(User).delete()
        db.session.commit()
        db.session.remove()

    yield

    with test_app.app_context():
        # 集成测试结束后清理本轮测试数据，
        # 但不删除数据库表结构。
        db.session.query(User).delete()
        db.session.commit()
        db.session.remove()