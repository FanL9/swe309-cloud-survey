# C1 证据

2026-11-23 在本地 Windows 电脑上实际运行时采集（Python 3.13.2，Flask 3.1.3）。图 C1-1 到 C1-6 使用一个全新的空数据库，按顺序操作；图 C1-7 到 C1-9 使用 `seed_demo.py` 生成的合成数据，用来展示增强功能。所有数据都是合成数据。

## 截图

| 图 | 文件 | 建议图注（英文） | 对应作业要求 |
|---|---|---|---|
| C1-1 | `c1-01-survey-page.jpg` | Fig. C1-1. The survey page running locally at http://127.0.0.1:8000. | 程序运行 |
| C1-2 | `c1-02-valid-rating-selected.jpg` | Fig. C1-2. A respondent selects Good and adds a synthetic comment. | 合法评分 |
| C1-3 | `c1-03-valid-rating-saved.jpg` | Fig. C1-3. The response is saved and its reference ID is shown. | 合法评分被保存 |
| C1-4 | `c1-04-invalid-rating-rejected.jpg` | Fig. C1-4. A tampered rating ("Excellent") is rejected with HTTP 400 and not stored. | 非法评分被拒绝 |
| C1-5 | `c1-05-stored-before-restart.jpg` | Fig. C1-5. Three stored responses before the server is stopped. | 存储的数据 |
| C1-6 | `c1-06-stored-after-restart.jpg` | Fig. C1-6. The same three responses after the server is started again. | 重启后数据保留 |
| C1-7 | `c1-07-dashboard.jpg` | Fig. C1-7. Staff dashboard with live metrics and charts (synthetic data). | 增强功能 |
| C1-8 | `c1-08-daily-report.jpg` | Fig. C1-8. Daily report for management, with the C-II batch result shown separately. | 增强功能 |
| C1-9 | `c1-09-filter-poor.jpg` | Fig. C1-9. Staff response list filtered to Poor ratings. | 增强功能 |
| C1-10 | （待补） | Fig. C1-10. The exported CSV stored in XMDrive. | CSV 已上传 XMDrive |

截图来自浏览器预览，宽度 800 像素。报告里需要更清晰的图，可以按同样步骤用 Win+Shift+S 重新截取。

## 文字证据

| 文件 | 内容 |
|---|---|
| `db-before-restart.txt` | 重启前直接查询 SQLite `responses` 表的结果（3 条） |
| `db-after-restart.txt` | 重启后再次查询，同样 3 条，内容一致 |
| `app-log.txt` | 本次运行的完整日志（已去掉本机路径）。可以看到：第 1 条通过表单提交成功（303）；`Excellent` 两次被拒绝（400，第一次是修改提示框样式前的截图尝试）；2 条通过 API 提交成功（201）；小写 `good` 被拒绝（400）；重启时启动日志显示 `responses=3` |
| `pytest-output.txt` | 67 个自动测试全部通过 |
| `source-structure.txt` | 源代码文件结构 |
| `../../data/exports/c1-responses-20261123.csv` | 导出的 CSV（3 条，字段 `response_id,rating,submitted_at`），这就是要上传到 XMDrive 的文件 |

日志说明（可直接用在报告里）：*The log shows each request with its status code, the accepted submissions with their response IDs, the rejected values with the reason `invalid_rating`, and the restart line reporting three stored responses.*

## 还需要成员本人补充

1. **图 C1-10：XMDrive 上传截图**。用学校账号登录 box.xmu.edu.my，上传 `data/exports/c1-responses-20261123.csv`，截取能看到文件名的页面，保存为 `c1-10-xmdrive-upload.png`。截图里不要露出学号以外的个人信息。
2. **（可选）代码结构截图**。作业要求"程序运行加源代码结构"，可以在 VS Code 里展开 `app/` 文件夹，和运行中的页面并排截一张图。`source-structure.txt` 可作为补充。
3. **（可选）终端截图**。如果希望数据库和日志也用截图展示，在 `app/` 下运行下面的命令，再截终端：

```powershell
.venv\Scripts\python -c "import sqlite3; [print(r) for r in sqlite3.connect('instance/evidence-run/survey.db').execute('SELECT * FROM responses')]"
```

本次取证用的数据库保存在 `app/instance/evidence-run/survey.db`（不提交到仓库）。
