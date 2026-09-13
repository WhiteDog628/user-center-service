import allure
import requests

from tests.allure_utils import attach_json


@allure.epic("用户中心 HTTP 接口自动化")
@allure.feature("系统服务")
@allure.story("健康检查")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("健康检查接口返回服务正常状态")
def test_health_http(base_url):
    url = f"{base_url}/api/health"

    with allure.step("通过 requests 发送健康检查 HTTP 请求"):
        attach_json(
            "请求信息",
            {
                "method": "GET",
                "url": url
            }
        )

        response = requests.get(
            url,
            timeout=5
        )

        attach_json(
            "响应结果",
            {
                "status_code": response.status_code,
                "body": response.json()
            }
        )

    with allure.step("校验 HTTP 状态码和服务状态"):
        assert response.status_code == 200

        data = response.json()

        assert data["code"] == 0
        assert data["message"] == "success"
        assert data["data"]["status"] == "UP"