# C1 应用代码

负责人：Member 4。Flask 3.1 + SQLite，实现问卷提交、服务端评分校验、持久化、日志和 CSV 导出。
增强功能（后续）：员工登录、ID 查询、筛选、指标卡、评分分布、每日趋势、每日报告及手机适配。

## 目录

```
app/
├── backend/            服务端代码
│   ├── __init__.py     create_app()：组装应用、请求日志、错误页
│   ├── config.py       从环境变量读取所有配置
│   ├── routes.py       页面、JSON 接口、健康检查
│   ├── validation.py   评分校验（只接受 Good / OK / Poor）
│   ├── storage.py      存储层（当前为 SQLite；以后可加 Firestore）
│   ├── export.py       CSV 导出
│   └── logging_setup.py
├── frontend/
│   ├── templates/      页面模板（base.html 统一引入样式）
│   └── static/css/     自定义样式
├── run.py              本地启动
├── wsgi.py             生产服务器入口（gunicorn）
├── export_csv.py       导出 CSV 的命令
├── requirements.txt    运行依赖
├── requirements-dev.txt 测试依赖
├── Dockerfile          容器镜像（Cloud Run）
└── .env.example        环境变量示例
```

运行时生成的 `instance/`（数据库、导出文件）和 `logs/` 已被 git 忽略，不会提交。

## 本地运行（Windows PowerShell）

```powershell
cd app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python run.py
```

打开 http://127.0.0.1:8000 。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 问卷页面 |
| POST | `/` | 表单提交；成功 303 跳转到感谢页，非法评分返回 400 |
| GET | `/thanks/<response_id>` | 感谢页，显示回复编号 |
| POST | `/api/responses` | JSON 提交，如 `{"rating": "Good", "comment": "..."}`；成功 201，非法 400 |
| GET | `/health` | 健康检查；正常 200，存储不可用 503 |

用 PowerShell 测试非法评分被拒绝：

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/responses -ContentType application/json -Body '{"rating":"Excellent"}'
```

## 导出 CSV

```powershell
python export_csv.py
```

文件写到 `instance/exports/responses-<时间>.csv`，字段为 `response_id,rating,submitted_at`，与 C3 一致。导出后手动上传到 XMDrive。

## 日志

同时输出到终端和 `logs/app.log`。每条请求记录方法、路径、状态码和耗时；提交成功记录回复编号和评分，被拒绝记录原因。评论内容和 IP 地址不写入日志（PDPA）。

## 测试

```powershell
python -m pytest ..\tests\app
```

## 部署

启动命令、端口、环境变量和健康检查见 `coordination/interfaces.md` 的 “C1 → C2” 一节。
