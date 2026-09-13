import uuid

import allure
import requests

from tests.allure_utils import attach_json


REQUEST_TIMEOUT = 5


def attach_request(
    method,
    url,
    headers=None,
    payload=None
):
    """
    将真实 HTTP 请求信息添加到 Allure 报告。

    Authorization、password 等敏感字段
    会由 attach_json 自动脱敏。
    """

    attach_json(
        "请求信息",
        {
            "method": method,
            "url": url,
            "headers": headers,
            "body": payload
        }
    )


def attach_response(response):
    """
    将真实 HTTP 响应信息添加到 Allure 报告。

    access_token 等敏感字段
    会由 attach_json 自动脱敏。
    """

    attach_json(
        "响应结果",
        {
            "status_code": response.status_code,
            "body": response.json()
        }
    )


def create_user_and_login(base_url):
    """
    创建测试用户并登录，返回真实 Access Token。

    Allure 附件中的 password 和 access_token
    会自动脱敏，但函数内部仍保留真实 Token，
    供后续鉴权请求使用。
    """

    suffix = uuid.uuid4().hex[:8]

    user = {
        "username": f"jwt_user_{suffix}",
        "email": f"jwt_user_{suffix}@test.com",
        "password": "123456"
    }

    register_url = (
        f"{base_url}/api/v1/auth/register"
    )

    with allure.step("注册 JWT 鉴权测试用户"):
        attach_request(
            "POST",
            register_url,
            payload=user
        )

        register_response = requests.post(
            register_url,
            json=user,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(register_response)

        assert register_response.status_code == 200

    login_url = (
        f"{base_url}/api/v1/auth/login"
    )

    login_payload = {
        "username": user["username"],
        "password": user["password"]
    }

    with allure.step("登录测试用户并获取 Access Token"):
        attach_request(
            "POST",
            login_url,
            payload=login_payload
        )

        login_response = requests.post(
            login_url,
            json=login_payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(login_response)

        assert login_response.status_code == 200

        login_data = login_response.json()

        assert login_data["code"] == 0
        assert "access_token" in login_data["data"]

    return login_data["data"]["access_token"]


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 携带有效 Token 获取当前用户成功")
def test_get_current_user_success_http(base_url):
    access_token = create_user_and_login(
        base_url
    )

    url = f"{base_url}/api/v1/users/me"

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        )
    }

    with allure.step(
        "携带有效 Access Token "
        "发送当前用户 HTTP 请求"
    ):
        attach_request(
            "GET",
            url,
            headers=headers
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step(
        "校验 HTTP 状态码和当前用户响应"
    ):
        assert response.status_code == 200

        data = response.json()

        assert data["code"] == 0
        assert (
            data["message"]
            == "get current user success"
        )

        assert "user_id" in data["data"]
        assert data["data"]["user_id"] is not None


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("HTTP 未携带 Token 访问受保护接口失败")
def test_get_current_user_without_token_http(
    base_url
):
    url = f"{base_url}/api/v1/users/me"

    with allure.step(
        "不携带 Authorization Header "
        "发送当前用户 HTTP 请求"
    ):
        attach_request(
            "GET",
            url
        )

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验未授权访问响应"):
        assert response.status_code == 401

        data = response.json()

        assert (
            data["msg"]
            == "Missing Authorization Header"
        )


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("用户模块")
@allure.story("JWT 鉴权")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("HTTP 携带非法 Token 访问受保护接口失败")
def test_get_current_user_with_invalid_token_http(
    base_url
):
    url = f"{base_url}/api/v1/users/me"

    headers = {
        "Authorization": (
            "Bearer invalid_token_123"
        )
    }

    with allure.step(
        "携带格式非法的 Access Token "
        "发送当前用户 HTTP 请求"
    ):
        attach_request(
            "GET",
            url,
            headers=headers
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验非法 Token 响应"):
        assert response.status_code == 422

        data = response.json()

        assert data["msg"] == "Not enough segments"