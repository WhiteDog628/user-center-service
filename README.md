# User Center Service

[![User Center CI](https://github.com/WhiteDog628/user-center-service/actions/workflows/ci.yml/badge.svg)](https://github.com/WhiteDog628/user-center-service/actions/workflows/ci.yml)

基于 **Flask + MySQL + pytest + requests + Allure + GitHub Actions** 构建的用户中心接口测试开发项目。

项目实现用户注册、登录、JWT 鉴权和健康检查等基础接口，并围绕接口质量建设了独立测试数据库、Flask test client 自动化测试、真实 HTTP 集成测试、Allure 测试结果、代码覆盖率统计以及 GitHub Actions CI 质量门禁。

## 项目亮点

| 能力 | 实现 |
| --- | --- |
| 接口服务 | Flask 用户注册、登录、JWT 鉴权、健康检查 |
| 数据存储 | MySQL 8.0 + SQLAlchemy |
| 环境隔离 | 开发数据库与自动化测试数据库独立 |
| 接口自动化 | pytest + Flask test client |
| HTTP 集成测试 | requests 调用独立 Flask Test Server |
| 测试数据管理 | pytest fixture 初始化并清理测试数据 |
| 测试结果 | Allure metadata、step、请求/响应附件 |
| 敏感信息保护 | Password、Token、Authorization 自动脱敏 |
| 代码覆盖率 | pytest-cov，当前语句覆盖率 **95.73%** |
| 质量门禁 | Coverage 低于 **90%** 时 CI 自动失败 |
| CI | GitHub Actions + MySQL 8 Service Container |
| 测试规模 | **25 条自动化测试用例** |

## 技术栈

| 类型 | 技术 |
| --- | --- |
| Web Framework | Flask 3.1 |
| ORM | Flask-SQLAlchemy / SQLAlchemy |
| Database | MySQL 8.0 |
| Authentication | Flask-JWT-Extended |
| Test Framework | pytest |
| HTTP Client | requests |
| Test Result | Allure |
| Coverage | pytest-cov |
| CI | GitHub Actions |
| Language | Python 3.12 |

## 项目结构

```text
user-center-service/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── __init__.py
│   └── extensions.py
├── tests/
│   ├── conftest.py
│   ├── allure_utils.py
│   ├── test_auth.py
│   └── test_user.py
├── integration_tests/
│   ├── conftest.py
│   ├── test_health_http.py
│   ├── test_auth_http.py
│   └── test_user_http.py
├── .env.example
├── config.py
├── pytest.ini
├── requirements.txt
├── run.py
└── run_test_server.py

```
## 核心接口

| Method | API | Description |
| --- | --- | --- |
| GET | `/api/health` | 服务健康检查 |
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录并获取 JWT |
| GET | `/api/v1/users/me` | JWT 鉴权接口 |

自动化测试覆盖注册成功、用户名或邮箱重复、必填字段缺失、登录成功、密码错误、用户不存在，以及有效 Token、Token 缺失和非法 Token 等场景。

## 自动化测试设计

项目采用两层接口自动化测试。

### Flask Test Client Tests

`tests/` 使用 Flask test client 直接调用应用，主要验证业务逻辑、参数校验、异常分支和 JWT 鉴权行为。

当前共 **12 条测试用例**，同时用于统计 `app/` 核心业务代码覆盖率。

### HTTP Integration Tests

`integration_tests/` 使用 `requests` 访问独立启动的 Flask Test Server：

```text
http://127.0.0.1:5001
```

用于验证真实 HTTP 请求经过路由、数据库访问到响应返回的完整链路。

当前共 **13 条测试用例**。

两层测试合计：

```text
12 + 13 = 25 automated test cases
```

## 测试环境隔离

开发环境和自动化测试环境使用独立数据库：

```text
Development Database:
user_center

Test Database:
user_center_service_test
```

分别通过：

```text
DATABASE_URL
TEST_DATABASE_URL
```

进行配置。

pytest fixture 在测试开始前确保表结构存在并清理历史测试数据，测试结束后仅清理数据、不删除表结构，从而避免：

- 自动化测试污染开发数据库
- 不同测试阶段之间残留测试数据
- 删除表结构后影响后续 HTTP 集成测试

## Allure 测试结果

测试用例使用 Allure 描述 Epic、Feature、Story、Severity、Title 和 Step，并将请求及响应信息作为附件写入测试结果。

敏感字段在写入 Allure 前进行脱敏，包括：

```text
password
access_token
token
authorization
```

例如：

```text
password: ***MASKED***
access_token: ***MASKED***
Authorization: ***MASKED***
```

生成 Allure Results：

```powershell
pytest tests -v --alluredir=allure-results --clean-alluredir
```

本地生成并打开 Allure HTML Report：

```powershell
allure generate allure-results -o allure-report --clean
allure open allure-report
```

> GitHub Actions 当前归档的是 Allure Results 原始结果文件，并未在 CI Runner 中生成 Allure HTML 页面。

## Coverage Quality Gate

项目使用 `pytest-cov` 对 `app/` 核心业务代码进行语句覆盖率统计。

当前结果：

```text
Statements: 117
Missing:      5
Covered:    112
Coverage: 95.73%
```

CI 设置最低覆盖率要求：

```text
Coverage >= 90%
```

如果覆盖率低于 90%，pytest 返回非零退出码，从而使 GitHub Actions Workflow 失败。

本地验证：

```powershell
pytest tests -v --cov=app --cov-report=term-missing --cov-fail-under=90
```

当前验证结果：

```text
Required test coverage of 90% reached.
Total coverage: 95.73%

12 passed
```

## GitHub Actions CI

代码 Push 或 Pull Request 到 `main` 分支后，GitHub Actions 自动执行：

```text
Push / Pull Request
        ↓
Checkout Repository
        ↓
Set up Python 3.12
        ↓
Install Dependencies
        ↓
MySQL 8.0 Service Container
        ↓
Flask Test Client Tests
        ↓
Coverage >= 90%
        ↓
Start Flask Test Server
        ↓
HTTP Integration Tests
        ↓
Upload Test Artifacts
```

CI Artifact 当前包含：

```text
allure-results/
coverage.xml
test-server.log
```

完整 CI 链路已在 GitHub Actions 中验证通过。

## 本地环境准备

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

根据本地 MySQL 环境配置：

```text
DATABASE_URL
TEST_DATABASE_URL
JWT_SECRET_KEY
```

真实数据库密码和 JWT Secret 仅保存在本地 `.env` 中，`.env` 不提交至 Git。

## 启动服务

启动开发服务：

```powershell
python run.py
```

默认地址：

```text
http://127.0.0.1:5000
```

## 运行测试

Flask test client：

```powershell
pytest tests -v
```

Coverage：

```powershell
pytest tests -v --cov=app --cov-report=term-missing --cov-fail-under=90
```

启动 HTTP 测试服务：

```powershell
python run_test_server.py
```

测试服务默认运行在：

```text
http://127.0.0.1:5001
```

然后在另一个终端执行：

```powershell
pytest integration_tests -v
```

## 当前验证结果

```text
Flask test-client tests: 12 passed
HTTP integration tests: 13 passed
Total automated tests: 25

Statement coverage: 95.73%
Coverage gate: 90%

GitHub Actions CI: Passed
```

## 项目定位

本项目重点不是单纯实现用户中心业务，而是围绕一个可运行的后端服务，实践接口测试设计、pytest fixture、真实 HTTP 集成测试、JWT 鉴权测试、MySQL 测试环境隔离、Allure 测试结果、代码覆盖率度量以及 GitHub Actions CI 质量门禁，形成可重复执行的接口自动化测试链路。
