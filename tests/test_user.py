def test_get_current_user_success(client, access_token):
    """
    携带有效 JWT Token 获取当前用户身份。
    """

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == 0
    assert data["message"] == "get current user success"

    assert "user_id" in data["data"]
    assert data["data"]["user_id"] is not None


def test_get_current_user_without_token(client):
    """
    未携带 JWT Token 访问受保护接口。
    """

    response = client.get(
        "/api/v1/users/me"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["msg"] == "Missing Authorization Header"


def test_get_current_user_with_invalid_token(client):
    """
    携带格式非法的 JWT Token 访问受保护接口。

    当前 Flask-JWT-Extended 对格式无法解析的 Token
    返回 HTTP 422。
    """

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid_token_123"
        }
    )

    assert response.status_code == 422

    data = response.get_json()

    assert data["msg"] == "Not enough segments"