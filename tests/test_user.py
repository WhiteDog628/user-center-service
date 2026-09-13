import allure


@allure.epic("用户中心接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("携带有效 Token 获取当前用户成功")
def test_get_current_user_success(
    client,
    access_token
):
    with allure.step("携带有效 Access Token 请求当前用户接口"):
        response = client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

    with allure.step("校验 HTTP 状态码和业务响应"):
        assert response.status_code == 200

        data = response.get_json()

        assert data["code"] == 0
        assert data["message"] == "get current user success"
        assert "user_id" in data["data"]
        assert data["data"]["user_id"] is not None


@allure.epic("用户中心接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("未携带 Token 访问受保护接口失败")
def test_get_current_user_without_token(client):
    with allure.step("不携带 Authorization Header 请求当前用户接口"):
        response = client.get(
            "/api/v1/users/me"
        )

    with allure.step("校验未授权访问响应"):
        assert response.status_code == 401

        data = response.get_json()

        assert data["msg"] == "Missing Authorization Header"


@allure.epic("用户中心接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("携带非法 Token 访问受保护接口失败")
def test_get_current_user_with_invalid_token(client):
    with allure.step("携带格式非法的 Access Token 请求当前用户接口"):
        response = client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": "Bearer invalid_token_123"
            }
        )

    with allure.step("校验非法 Token 响应"):
        assert response.status_code == 422

        data = response.get_json()

        assert data["msg"] == "Not enough segments"