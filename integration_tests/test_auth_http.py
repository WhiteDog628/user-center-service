import uuid

import allure
import pytest
import requests

from tests.allure_utils import attach_json


REQUEST_TIMEOUT = 5


def build_user(prefix):
    """
    生成唯一测试用户数据。
    """

    suffix = uuid.uuid4().hex[:8]

    return {
        "username": f"{prefix}_{suffix}",
        "email": f"{prefix}_{suffix}@test.com",
        "password": "123456"
    }


def attach_request(method, url, payload=None):
    """
    将真实 HTTP 请求信息添加到 Allure 报告。

    password 等敏感字段由 attach_json 自动脱敏。
    """

    attach_json(
        "请求信息",
        {
            "method": method,
            "url": url,
            "body": payload
        }
    )


def attach_response(response):
    """
    将真实 HTTP 响应信息添加到 Allure 报告。

    access_token 等敏感字段由 attach_json 自动脱敏。
    """

    attach_json(
        "响应结果",
        {
            "status_code": response.status_code,
            "body": response.json()
        }
    )


def register_user(base_url, user):
    """
    注册测试用户。

    主要用于登录等场景的前置条件准备。
    """

    return requests.post(
        f"{base_url}/api/v1/auth/register",
        json=user,
        timeout=REQUEST_TIMEOUT
    )


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 注册成功")
def test_register_success_http(base_url):
    user = build_user("register_success")
    url = f"{base_url}/api/v1/auth/register"

    with allure.step("通过 requests 发送用户注册 HTTP 请求"):
        attach_request(
            "POST",
            url,
            user
        )

        response = requests.post(
            url,
            json=user,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验注册成功响应"):
        assert response.status_code == 200

        data = response.json()

        assert data["code"] == 0
        assert data["message"] == "register success"
        assert data["data"]["username"] == user["username"]
        assert data["data"]["email"] == user["email"]
        assert "password_hash" not in data["data"]


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 注册失败：用户名重复")
def test_register_duplicate_username_http(base_url):
    first_user = build_user("duplicate_username")

    with allure.step("创建已存在的用户名"):
        first_response = register_user(
            base_url,
            first_user
        )

        assert first_response.status_code == 200

    second_user = {
        "username": first_user["username"],
        "email": (
            f"another_{uuid.uuid4().hex[:8]}"
            "@test.com"
        ),
        "password": "123456"
    }

    url = f"{base_url}/api/v1/auth/register"

    with allure.step("使用重复用户名再次发送注册请求"):
        attach_request(
            "POST",
            url,
            second_user
        )

        response = requests.post(
            url,
            json=second_user,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验用户名冲突响应"):
        assert response.status_code == 409

        data = response.json()

        assert data["code"] == 1001
        assert data["message"] == "username already exists"


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 注册失败：邮箱重复")
def test_register_duplicate_email_http(base_url):
    first_user = build_user("duplicate_email")

    with allure.step("创建已存在的邮箱"):
        first_response = register_user(
            base_url,
            first_user
        )

        assert first_response.status_code == 200

    second_user = {
        "username": f"user_b_{uuid.uuid4().hex[:8]}",
        "email": first_user["email"],
        "password": "123456"
    }

    url = f"{base_url}/api/v1/auth/register"

    with allure.step("使用重复邮箱再次发送注册请求"):
        attach_request(
            "POST",
            url,
            second_user
        )

        response = requests.post(
            url,
            json=second_user,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验邮箱冲突响应"):
        assert response.status_code == 409

        data = response.json()

        assert data["code"] == 1002
        assert data["message"] == "email already exists"


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("HTTP 注册失败：缺少密码")
def test_register_missing_password_http(base_url):
    user = build_user("register_missing_password")

    payload = {
        "username": user["username"],
        "email": user["email"]
    }

    url = f"{base_url}/api/v1/auth/register"

    with allure.step("发送缺少 password 字段的 HTTP 注册请求"):
        attach_request(
            "POST",
            url,
            payload
        )

        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验缺少密码响应"):
        assert response.status_code == 400

        data = response.json()

        assert data["code"] == 1
        assert data["message"] == "password is required"


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("HTTP 登录成功并获取 Access Token")
def test_login_success_http(base_url):
    user = build_user("login_success")

    with allure.step("注册登录测试用户"):
        register_response = register_user(
            base_url,
            user
        )

        assert register_response.status_code == 200

    payload = {
        "username": user["username"],
        "password": user["password"]
    }

    url = f"{base_url}/api/v1/auth/login"

    with allure.step("通过 requests 发送用户登录 HTTP 请求"):
        attach_request(
            "POST",
            url,
            payload
        )

        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验登录成功响应和 Access Token"):
        assert response.status_code == 200

        data = response.json()

        assert data["code"] == 0
        assert data["message"] == "login success"

        assert "access_token" in data["data"]
        assert data["data"]["access_token"]

        assert data["data"]["token_type"] == "Bearer"

        assert (
            data["data"]["user"]["username"]
            == user["username"]
        )

        assert (
            "password_hash"
            not in data["data"]["user"]
        )


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 登录失败：密码错误")
def test_login_wrong_password_http(base_url):
    user = build_user("wrong_password")

    with allure.step("注册登录测试用户"):
        register_response = register_user(
            base_url,
            user
        )

        assert register_response.status_code == 200

    payload = {
        "username": user["username"],
        "password": "wrong_password"
    }

    url = f"{base_url}/api/v1/auth/login"

    with allure.step("使用错误密码发送 HTTP 登录请求"):
        attach_request(
            "POST",
            url,
            payload
        )

        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验密码错误响应"):
        assert response.status_code == 401

        data = response.json()

        assert data["code"] == 2002
        assert data["message"] == "password incorrect"


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("HTTP 登录失败：用户不存在")
def test_login_user_not_found_http(base_url):
    payload = {
        "username": (
            f"not_exist_{uuid.uuid4().hex[:8]}"
        ),
        "password": "123456"
    }

    url = f"{base_url}/api/v1/auth/login"

    with allure.step("使用不存在的用户发送 HTTP 登录请求"):
        attach_request(
            "POST",
            url,
            payload
        )

        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验用户不存在响应"):
        assert response.status_code == 401

        data = response.json()

        assert data["code"] == 2001
        assert data["message"] == "user not found"


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize(
    "payload, expected_message",
    [
        (
            {"password": "123456"},
            "username is required"
        ),
        (
            {"username": "test_user"},
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
    if expected_message == "username is required":
        allure.dynamic.title(
            "HTTP 登录失败：缺少用户名"
        )
    else:
        allure.dynamic.title(
            "HTTP 登录失败：缺少密码"
        )

    url = f"{base_url}/api/v1/auth/login"

    with allure.step("发送缺少必填字段的 HTTP 登录请求"):
        attach_request(
            "POST",
            url,
            payload
        )

        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        attach_response(response)

    with allure.step("校验参数校验失败响应"):
        assert response.status_code == 400

        data = response.json()

        assert data["code"] == 1
        assert data["message"] == expected_message