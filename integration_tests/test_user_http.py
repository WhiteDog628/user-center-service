import uuid

import requests


REQUEST_TIMEOUT = 5


def create_user_and_login(base_url):
    """
    创建随机测试用户并登录，
    返回有效 JWT Access Token。
    """

    suffix = uuid.uuid4().hex[:8]

    user = {
        "username": f"jwt_user_{suffix}",
        "email": f"jwt_user_{suffix}@test.com",
        "password": "123456"
    }

    register_response = requests.post(
        f"{base_url}/api/v1/auth/register",
        json=user,
        timeout=REQUEST_TIMEOUT
    )

    assert register_response.status_code == 200

    login_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={
            "username": user["username"],
            "password": user["password"]
        },
        timeout=REQUEST_TIMEOUT
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert login_data["code"] == 0
    assert "access_token" in login_data["data"]

    return login_data["data"]["access_token"]


def test_get_current_user_success_http(base_url):
    """
    携带有效 JWT Token 访问受保护接口。
    """

    access_token = create_user_and_login(
        base_url
    )

    response = requests.get(
        f"{base_url}/api/v1/users/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            )
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == 0

    assert (
        data["message"]
        == "get current user success"
    )

    assert "user_id" in data["data"]

    assert data["data"]["user_id"] is not None


def test_get_current_user_without_token_http(base_url):
    """
    不携带 JWT Token 访问受保护接口。
    """

    response = requests.get(
        f"{base_url}/api/v1/users/me",
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 401

    data = response.json()

    assert (
        data["msg"]
        == "Missing Authorization Header"
    )


def test_get_current_user_with_invalid_token_http(
    base_url
):
    """
    携带格式非法的 JWT Token 访问受保护接口。

    当前 Flask-JWT-Extended 默认返回 HTTP 422。
    """

    response = requests.get(
        f"{base_url}/api/v1/users/me",
        headers={
            "Authorization": (
                "Bearer invalid_token_123"
            )
        },
        timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 422

    data = response.json()

    assert data["msg"] == "Not enough segments"