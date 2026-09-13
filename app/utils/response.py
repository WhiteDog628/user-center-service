from flask import jsonify


def success_response(data=None, message="success"):
    """
    成功响应。

    返回统一格式：
    {
        "code": 0,
        "message": "success",
        "data": {}
    }
    """

    return jsonify(
        {
            "code": 0,
            "message": message,
            "data": data
        }
    ), 200


def error_response(
    message="error",
    code=1,
    status_code=400
):
    """
    错误响应。

    参数：
        message:
            错误描述

        code:
            业务错误码

        status_code:
            HTTP 状态码
    """

    return jsonify(
        {
            "code": code,
            "message": message,
            "data": None
        }
    ), status_code