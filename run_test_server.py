from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig


# 使用独立测试配置创建 Flask 应用
app = create_app(TestConfig)


def initialize_test_database():
    """
    初始化 HTTP 集成测试数据库。

    测试服务启动时确保所需数据表存在。
    """

    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    initialize_test_database()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )