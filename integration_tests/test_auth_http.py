import uuid

import pytest
import requests


REQUEST_TIMEOUT = 5


def build_user(prefix="http_user"):
    """
    生成唯一测试用户数据，
    避免多次执行测试时发生用户名或邮箱冲突。
    """

    suffix = uuid.uuid4().hex[:8]

    username = f"{prefix}_{suffix}"

    return {
        "username": username,
        "email": f"{username}@test.com",
        "password": "123456"
    }


def register_user(base_url, user):
    """
    调用真实 HTTP 注册接口。
    """

    return requests.post(
        f"{base_url}/api/v1/auth/register",
        json=user,
        timeout=REQUEST_TIMEOUT
    )


def test_register_success_http(base_url):
    """
    HTTP 注册成功测试。
    """

    user = build_user("register_success")

    response = register_user(
        base_url,
        user
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == 0
    assert data["message"] == "register success"

    assert (
        data["data"]["username"]
        == user["username"]
    )

    assert (
        data["data"]["email"]
        == user["email"]
    )

    assert "password_hash" not in data["data"]


def test_register_duplicate_username_http(base_url):
    """
    HTTP 注册用户名重复测试。
    """

    user = build_user("duplicate_username")

    first_response = register_user(
        base_url,
        user
    )

    assert first_response.status_code == 200

    second_user = {
        "username": user["username"],
        "email": (
            f"another_{uuid.uuid4().hex[:8]}"
            "@test.com"
        ),
        "password": "123456"
    }

    response = register_user(
        base_url,
        second_user
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == 1001
    assert data["message"] == "username already exists"


def test_register_duplicate_email_http(base_url):
    """
    HTTP 注册邮箱重复测试。
    """

    user = build_user("duplicate_email")

    first_response = register_user(
        base_url,
        user
    )

    assert first_response.status_code == 200

    second_user = {
        "username": (
            f"other_user_{uuid.uuid4().hex[:8]}"
        ),
        "email": user["email"],
        "password": "123456"
    }

    response = register_user(
        base_url,
        second_user
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == 1002
    assert data["message"] == "email already exists"


def test_register_missing_password_http(base_url):
    """
    HTTP 注册缺少密码测试。
    """

    suffix = uuid.uuid4().hex[:8]

    response = requests.post(
        f"{base_url}/api/v1/auth/register",
        json={
            "username": f"missing_pwd_{suffix}",
            "email": f"missing_pwd_{suffix}@test.com"
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == 1
    assert data["message"] == "password is required"


def test_login_success_http(base_url):
    """
    HTTP 登录成功测试。
    """

    user = build_user("login_success")

    register_response = register_user(
        base_url,
        user
    )

    assert register_response.status_code == 200

    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={
            "username": user["username"],
            "password": user["password"]
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == 0
    assert data["message"] == "login success"

    assert "access_token" in data["data"]

    assert (
        data["data"]["access_token"]
        is not None
    )

    assert (
        data["data"]["token_type"]
        == "Bearer"
    )

    assert (
        data["data"]["user"]["username"]
        == user["username"]
    )

    assert (
        "password_hash"
        not in data["data"]["user"]
    )


def test_login_wrong_password_http(base_url):
    """
    HTTP 登录密码错误测试。
    """

    user = build_user("wrong_password")

    register_response = register_user(
        base_url,
        user
    )

    assert register_response.status_code == 200

    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={
            "username": user["username"],
            "password": "wrong_password"
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 401

    data = response.json()

    assert data["code"] == 2002
    assert data["message"] == "password incorrect"


def test_login_user_not_found_http(base_url):
    """
    HTTP 登录用户不存在测试。
    """

    username = (
        f"not_exist_{uuid.uuid4().hex[:8]}"
    )

    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={
            "username": username,
            "password": "123456"
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 401

    data = response.json()

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
def test_login_missing_required_field_http(
    base_url,
    payload,
    expected_message
):
    """
    HTTP 登录必填参数缺失测试。
    """

    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == 1
    assert data["message"] == expected_message