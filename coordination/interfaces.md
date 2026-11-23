# 模块接口约定（待团队确认）

## C1 → C3

CSV 字段（已按 C3 现有数据对齐）：`response_id,rating,submitted_at`。

- `rating` 仅允许 `Good`、`OK`、`Poor`，精确匹配，不去空格、不改大小写（与 C3 规则一致）。
- `response_id` 由应用生成，格式 `RYYYYMMDD-XXXXXX`（例：`R20261123-K7Q2XM`），全局唯一。
- `submitted_at` 为带时区 ISO 8601，固定马来西亚时间 `+08:00`，精确到秒（例：`2026-11-23T14:05:09+08:00`）。
- 导出不包含评论等其他字段（数据最小化，符合 PDPA）。
- 导出命令：在 `app/` 下运行 `python export_csv.py`，文件 UTF-8、首行为表头。

## C3 → C1

约定聚合文件字段、文件格式、存放路径、统计日期、更新时间和无效/重复记录的计数方式。看板区分原始实时数据和批处理结果。

C1 报告页暂定读取 `rating,count` 格式的 CSV（即 C3 现有 `counts.csv`），路径由环境变量 `C3_COUNTS_PATH` 指定。

## C1 → C2

| 项目 | 约定 |
|---|---|
| 框架 / 语言 | Flask 3.1，Python 3.12 或 3.13 |
| 部署根目录 | `app/`（含 `backend/`、`frontend/`、`requirements.txt`、`Dockerfile`） |
| 依赖安装 | `pip install -r requirements.txt` |
| 生产启动命令 | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --access-logfile - wsgi:app` |
| 本地启动命令 | `python run.py`（Windows 可用） |
| 容器 | `app/Dockerfile`，默认监听 8080，适用于 Cloud Run |
| 健康检查 | `GET /health`，正常返回 200 和 `{"status": "ok"}`，存储不可用返回 503 |
| 日志 | 始终输出到标准输出（云平台自动收集）；`LOG_FILE` 非空时另写文件 |
| 持久化 | 当前为 SQLite 单文件，路径由 `DATABASE_PATH` 指定 |

### 环境变量

| 变量 | 默认值 | 说明 | 何时需要 |
|---|---|---|---|
| `APP_ENV` | `development` | 云上设为 `production` | 现在 |
| `HOST` | `127.0.0.1` | 云上设为 `0.0.0.0` | 现在 |
| `PORT` | `8000`（容器内 `8080`） | 监听端口，Cloud Run 会自动注入 | 现在 |
| `DATABASE_PATH` | `app/instance/survey.db` | SQLite 文件路径 | 现在 |
| `LOG_LEVEL` | `INFO` | 日志级别 | 现在 |
| `LOG_FILE` | `app/logs/app.log` | 日志文件；设为空字符串则只输出到标准输出 | 现在 |
| `EXPORT_DIR` | `app/instance/exports` | CSV 导出目录 | 现在 |
| `SECRET_KEY` | 开发环境随机生成 | 会话签名密钥，生产环境必须设置，放在密钥管理服务里；多实例必须相同 | 现在（员工登录已上线） |
| `STAFF_USERNAME` | 空 | 员工后台用户名；生产环境未设置则后台不可用 | 现在 |
| `STAFF_PASSWORD_HASH` | 空 | 员工密码的哈希值（不存明文），在 `app/` 下运行 `python hash_password.py` 生成；放在密钥管理服务里 | 现在 |
| `STORAGE_BACKEND` | `sqlite` | 存储后端；`firestore` 为预留值，尚未实现 | 若改用 Firestore |
| `C3_COUNTS_PATH` | 空 | C3 聚合结果 CSV 路径 | 第 5 步 |

### 已知限制（需 C2 决定）

Cloud Run 的实例磁盘是临时的，实例重启或缩到零后 SQLite 数据会丢失。若在 Cloud Run 上演示，需要：
1. 接受数据不持久（仅演示用），或
2. 改用 Firestore（B1 推荐的存储），需在 `backend/storage.py` 增加一个实现，路由代码不用改，或
3. 选用带持久磁盘的平台（如 PythonAnywhere 免费版、Azure App Service）。

## B1/B2 ↔ C2

云平台比较、推荐架构和实际部署应保持一致；免费额度、正常月费、已实现与仅设计功能分别说明。
