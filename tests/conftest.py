import uuid

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig


@pytest.fixture(scope="session")
def app():
    """
    创建 pytest 专用 Flask 应用。

    使用 TestConfig，
    数据库连接指向 user_center_service_test。
    """

    app = create_app(TestConfig)

    with app.app_context():
        # 测试开始前重建测试数据库表，
        # 保证测试环境结构确定且干净。
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        # 整个测试会话结束后清理测试数据库。
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    创建 Flask 测试客户端。

    每个测试函数执行前清空 users 表，
    保证测试用例之间互不污染。
    """

    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()


@pytest.fixture
def register_user(client):
    """
    创建随机测试用户。

    返回用户名、邮箱和密码，
    供登录及鉴权测试复用。
    """

    username = f"test_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"
    password = "123456"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return {
        "username": username,
        "email": email,
        "password": password
    }


@pytest.fixture
def access_token(client, register_user):
    """
    登录测试用户并获取 JWT Access Token。
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": register_user["username"],
            "password": register_user["password"]
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == 0
    assert "access_token" in data["data"]

    return data["data"]["access_token"]