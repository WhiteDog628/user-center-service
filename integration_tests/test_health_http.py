import requests


def test_health_http(base_url):
    """
    使用 requests 通过真实 HTTP 请求
    验证 Flask 健康检查接口。
    """

    response = requests.get(
        f"{base_url}/api/health",
        timeout=5
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == 0
    assert data["message"] == "success"
    assert data["data"]["status"] == "UP"