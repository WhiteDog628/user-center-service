import uuid

import pytest


def test_register_success(client):
    """
    注册成功测试。
    """

    username = f"pytest_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == 0
    assert data["message"] == "register success"
    assert data["data"]["username"] == username


def test_register_duplicate_username(client):
    """
    注册用户名重复测试。
    """

    username = f"duplicate_user_{uuid.uuid4().hex[:8]}"

    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"another_{uuid.uuid4().hex[:8]}@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["code"] == 1001
    assert data["message"] == "username already exists"


def test_register_duplicate_email(client):
    """
    注册邮箱重复测试。
    """

    email = f"duplicate_{uuid.uuid4().hex[:8]}@test.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_a_{uuid.uuid4().hex[:8]}",
            "email": email,
            "password": "123456"
        }
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_b_{uuid.uuid4().hex[:8]}",
            "email": email,
            "password": "123456"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["code"] == 1002
    assert data["message"] == "email already exists"


def test_register_missing_password(client):
    """
    注册缺少密码测试。
    """

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"missing_pwd_{uuid.uuid4().hex[:8]}",
            "email": f"missing_pwd_{uuid.uuid4().hex[:8]}@test.com"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["code"] == 1
    assert data["message"] == "password is required"


def test_login_success(client, register_user):
    """
    登录成功测试。
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
    assert data["message"] == "login success"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "Bearer"


def test_login_wrong_password(client, register_user):
    """
    登录密码错误测试。
    """

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": register_user["username"],
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["code"] == 2002
    assert data["message"] == "password incorrect"


def test_login_user_not_found(client):
    """
    登录用户不存在测试。
    """

    username = f"not_exist_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": "123456"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["code"] == 2001
    assert data["message"] == "user not found"


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        (
            {
                "password": "123456"
            },
            "username is required"
        ),
        (
            {
                "username": "test_user"
            },
            "password is required"
        )
    ],
    ids=[
        "missing_username",
        "missing_password"
    ]
)
def test_login_missing_required_field(
    client,
    payload,
    expected_message
):
    """
    登录必填参数缺失测试。

    参数化覆盖：
    1. 缺少 username；
    2. 缺少 password。
    """

    response = client.post(
        "/api/v1/auth/login",
        json=payload
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["code"] == 1
    assert data["message"] == expected_message