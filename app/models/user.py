from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    """
    用户数据模型。

    对应 MySQL 中的 users 表。
    """

    __tablename__ = "users"

    # 用户唯一标识
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    # 登录用户名
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # 用户邮箱
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    # 密码哈希值，不保存明文密码
    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # 用户昵称，可为空
    nickname = db.Column(
        db.String(50),
        nullable=True
    )

    # 创建时间
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # 最后更新时间
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def set_password(self, password):
        """
        对明文密码进行哈希处理后保存。
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        校验输入的明文密码是否与已保存的密码哈希匹配。
        """
        return check_password_hash(
            self.password_hash,
            password
        )

    def to_dict(self):
        """
        将用户对象转换为可返回给客户端的字典。

        注意：
        不返回 password_hash，避免敏感数据泄露。
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }