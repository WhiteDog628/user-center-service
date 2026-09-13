import uuid

import allure
import pytest


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("用户注册成功")
def test_register_success(client):
    username = f"pytest_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@test.com"

    with allure.step("发送用户注册请求"):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": "123456"
            }
        )

    with allure.step("校验 HTTP 状态码和业务响应"):
        assert response.status_code == 200

        data = response.get_json()

        assert data["code"] == 0
        assert data["message"] == "register success"
        assert data["data"]["username"] == username


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("注册失败：用户名重复")
def test_register_duplicate_username(client):
    username = f"duplicate_user_{uuid.uuid4().hex[:8]}"

    with allure.step("创建已存在的用户名"):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "123456"
            }
        )

    with allure.step("使用相同用户名再次注册"):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"another_{uuid.uuid4().hex[:8]}@test.com",
                "password": "123456"
            }
        )

    with allure.step("校验用户名冲突响应"):
        assert response.status_code == 409

        data = response.get_json()

        assert data["code"] == 1001
        assert data["message"] == "username already exists"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("注册失败：邮箱重复")
def test_register_duplicate_email(client):
    email = f"duplicate_{uuid.uuid4().hex[:8]}@test.com"

    with allure.step("创建已存在的邮箱"):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": f"user_a_{uuid.uuid4().hex[:8]}",
                "email": email,
                "password": "123456"
            }
        )

    with allure.step("使用相同邮箱再次注册"):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"user_b_{uuid.uuid4().hex[:8]}",
                "email": email,
                "password": "123456"
            }
        )

    with allure.step("校验邮箱冲突响应"):
        assert response.status_code == 409

        data = response.get_json()

        assert data["code"] == 1002
        assert data["message"] == "email already exists"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("注册失败：缺少密码")
def test_register_missing_password(client):
    with allure.step("发送缺少 password 字段的注册请求"):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"missing_pwd_{uuid.uuid4().hex[:8]}",
                "email": f"missing_pwd_{uuid.uuid4().hex[:8]}@test.com"
            }
        )

    with allure.step("校验缺少必填字段响应"):
        assert response.status_code == 400

        data = response.get_json()

        assert data["code"] == 1
        assert data["message"] == "password is required"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("用户登录成功并获取 Access Token")
def test_login_success(client, register_user):
    with allure.step("使用已注册用户发送登录请求"):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": register_user["username"],
                "password": register_user["password"]
            }
        )

    with allure.step("校验登录响应和 Access Token"):
        assert response.status_code == 200

        data = response.get_json()

        assert data["code"] == 0
        assert data["message"] == "login success"
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("登录失败：密码错误")
def test_login_wrong_password(client, register_user):
    with allure.step("使用错误密码发送登录请求"):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": register_user["username"],
                "password": "wrong_password"
            }
        )

    with allure.step("校验密码错误响应"):
        assert response.status_code == 401

        data = response.get_json()

        assert data["code"] == 2002
        assert data["message"] == "password incorrect"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("登录失败：用户不存在")
def test_login_user_not_found(client):
    username = f"not_exist_{uuid.uuid4().hex[:8]}"

    with allure.step("使用不存在的用户名发送登录请求"):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": "123456"
            }
        )

    with allure.step("校验用户不存在响应"):
        assert response.status_code == 401

        data = response.get_json()

        assert data["code"] == 2001
        assert data["message"] == "user not found"


@allure.epic("用户中心接口自动化")
@allure.feature("认证模块")
@allure.story("用户登录")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("登录失败：缺少必填字段")
@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"password": "123456"}, "username is required"),
        ({"username": "test_user"}, "password is required")
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
    with allure.step("发送缺少必填字段的登录请求"):
        response = client.post(
            "/api/v1/auth/login",
            json=payload
        )

    with allure.step("校验参数校验失败响应"):
        assert response.status_code == 400

        data = response.get_json()

        assert data["code"] == 1
        assert data["message"] == expected_message