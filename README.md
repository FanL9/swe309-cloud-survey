# SWE309 Cloud Survey Platform

问卷平台课程项目协作仓库，包含研究与架构设计、Flask 原型、PythonAnywhere 云端演示和 PySpark 数据处理。进度更新：2026-11-25。

## 当前完成情况

| 模块 | 负责人 | 已完成工作与证据 |
|---|---|---|
| A-I、B-I | Li Jingqi | NIST 概念分析、EC2 与 Cloud Run 比较、区域成本表与推荐初稿：[A-I](docs/A1-cloud-concepts/A1.docx)、[B-I](docs/B1-platform-comparison/B1.docx)。原始价格计算器导出文件仍需集中归档。 |
| A-II、B-II | Fan Li | 云参与者与服务模型、架构、安全、弹性及 OpenStack 替代方案初稿：[论文](submissions/final/member2/member2-report.pdf)、[图源](diagrams/member2/)。已整理本地进度报告并核对作业要求和仓库证据，提交版尚待上传。 |
| A-III、C3 | Wang Zhaoyang | 基础系统研究、手算与 PySpark 作业完成。Table 2 的 Good/OK/Poor 为 5/3/2；扩展数据 40 条，接受 30 条（12/10/8），排除 5 条重复及 5 条无效评分：[手算](docs/C3-data-processing/hand-trace.md)、[运行验证](evidence/C3/verification.json)。 |
| C1 | Cheng Shaozhe | Flask/SQLite 原型、评分校验、重启持久化、日志、CSV 导出与 XMDrive 上传、员工后台及批处理结果展示：[证据](evidence/C1/README.md)。[测试记录](evidence/C1/pytest-output.txt)显示 67 项通过；[CI](.github/workflows/c1-app.yml)包含测试和 Docker 构建检查。 |
| C2 | Zhu Changxu | 部署计划和 PythonAnywhere HTTPS 演示，六条数据在重载后保留，登录权限、CSRF、请求日志有验证记录：[部署报告](docs/C2-cloud-deployment/report.md)、[证据](evidence/C2/README.md)、[检查记录](tests/deployment/README.md)。 |

以上为仓库已有文件和运行记录所支持的完成情况，不代表所有最终提交材料已完成。五位成员的进度报告暂定贡献比例均为 **20%**，合计 **100%**；最终各评分组件的贡献记录需另行完成并签名。

### 内部分工与正式作业编号

**C1、C2、C3 是为均衡工作量采用的内部拆分。正式作业 C-I 对应 C1 系统实现及 XMDrive + C2 部署计划与可选云端演示；C-II 对应 C3 数据处理。** 它们不是三个独立的正式评分任务。

## 已演示与仅设计的边界

- 已演示：本地 Flask/SQLite、PythonAnywhere 部署、CSV 手动上传 XMDrive、单机 PySpark `local[2]` 处理和后台读取已有批处理结果。
- 拟采用的生产托管平台：Google Cloud Run，公有云/serverless PaaS，Singapore `asia-southeast1`。
- 存储尚待统一：B-I 推荐 Firestore，旧 B-II 文档使用 Cloud SQL。当前进度报告以 Firestore 为暂定方案，需确认后统一原文、架构图、成本和部署计划；尚未实现 Firestore 后端。
- 尚未演示：Cloud Run 实际部署、生产峰值容量、自动每日导出/调度，以及完整的按日 C1 → C3 → 报表流程。现有看板能读取结果文件，不等于自动管线已经完成。
- 作业必需的是本地原型、XMDrive 证据和云部署计划；实际公有云部署是可选补充，不要求购买云服务。自动管线和托管存储迁移属于计划或增强内容。

## 已遇问题、后续计划与风险

以下为进度报告的计划目标，每项列一位主要负责人。

| 目标日期 | 主要负责人 | 已遇问题 / 下一步 | 风险与应对 |
|---|---|---|---|
| 11 月 27 日 | Fan Li | 解决 Firestore/Cloud SQL 文档不一致，统一 B-I、B-II、架构图及 C2 计划。 | 避免按不同设计实施；确定存储后联合检查成本和访问控制。 |
| 11 月 30 日 | Li Jingqi | 归档两家厂商原始计算器导出，核对 B-I 的 Firestore 输入。 | 避免低估费用；保留日期、区域、假设与未计入项目。 |
| 12 月 10 日 | Cheng Shaozhe | Cloud Run 的临时磁盘不能持久保存本地 SQLite；制定外部存储和备份方案。 | 防止数据丢失；使用外部存储并验证重启持久化。 |
| 12 月 12 日 | Wang Zhaoyang | C3 未按日期过滤；使用按日 C1 导出，核对员工报表集成。 | 防止每日统计范围错误；与独立手算核对。 |
| 12 月 20 日 | Zhu Changxu | 排练演示，核对 C2 证据与运行版本。 | 网络故障或免费账号到期时，使用已验证的本地演示和备用录屏。 |

Fan Li 牵头于 12 月 22 日前核对合并报告、签名贡献记录和幻灯片。仍需核查完整报告字数、引用、截图、附录及评分表。报告与 PPT 截止：**2026-12-23 23:59**；展示：**2026-12-24**。进度报告截止：**2026-11-27 23:59**，课程当地时间以 Moodle 为准。

## 目录与协作

- `app/`：原型源代码；`tests/`：应用、处理及部署检查。
- `docs/`：各模块文稿；`diagrams/`：架构图与可编辑图源。
- `deploy/`：部署说明；`processing/`：Spark/Hive 处理代码。
- `data/`：合成输入、导出和聚合结果；`evidence/`：截图、测试和运行记录。
- `references/`：来源、版本、区域、查询日期与成本依据。
- `submissions/`：进度报告、最终报告、PPT 的已核对提交版本。
- `coordination/`：任务及接口约定；其中旧进度勾选仍需同步，以本页链接的实际证据为依据。

常规协作从 main 创建 feature 分支并通过 Pull Request 合并；先对齐 [接口约定](coordination/interfaces.md)。仅使用合成数据，不提交密码、云密钥、真实个人数据或本地数据库；运行日志须脱敏。本文是项目状态与组织说明，不替代课程要求。
