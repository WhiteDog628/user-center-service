import json

import allure


SENSITIVE_KEYS = {
    "password",
    "access_token",
    "token",
    "authorization"
}


def sanitize_data(data):
    """
    递归脱敏测试数据。

    对密码、Token、Authorization 等敏感字段进行替换，
    避免敏感信息直接出现在 Allure 报告中。
    """

    if isinstance(data, dict):
        sanitized = {}

        for key, value in data.items():
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = sanitize_data(value)

        return sanitized

    if isinstance(data, list):
        return [
            sanitize_data(item)
            for item in data
        ]

    return data


def attach_json(name, data):
    """
    将 JSON 数据脱敏后添加到 Allure 报告附件。
    """

    sanitized_data = sanitize_data(data)

    allure.attach(
        json.dumps(
            sanitized_data,
            ensure_ascii=False,
            indent=2
        ),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )