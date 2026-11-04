# SWE309 Cloud Survey Platform

问卷系统、可视化后台、真实云部署和数据处理的协作仓库。当前只有项目骨架，尚未实现应用或部署。

## 文件夹与分工

| 模块 | 文档位置 | 代码/操作位置 | 负责人（按已确认分工） |
|---|---|---|---|
| A1 云计算概念 | docs/A1-cloud-concepts/ | 无 | Member 1 |
| A2 云模型与参与者 | docs/A2-models-and-actors/ | 无 | Member 2 |
| A3 历史系统与现代技术 | docs/A3-foundational-systems/ | 无 | Member 3 |
| B1 云平台比较 | docs/B1-platform-comparison/ | 无 | Member 1 |
| B2 架构设计 | docs/B2-architecture/ | diagrams/ | Member 2 |
| C1 系统开发 | docs/C1-system-implementation/ | app/、tests/app/ | Member 4 |
| C2 云部署 | docs/C2-cloud-deployment/ | deploy/、tests/deployment/ | Member 5 |
| C3 数据处理 | docs/C3-data-processing/ | processing/、tests/processing/ | Member 3 |

C1/C2/C3 为内部工作编号；正式报告 C-I 对应 C1+C2，C-II 对应 C3。

## 其他目录

- data/：合成输入、CSV 导出、聚合结果。
- evidence/：按 C1/C2/C3 整理有标注的证据。
- references/：官方资料、版本、区域、查询日期和价格计算记录。
- submissions/：进度报告、最终报告、PPT 的提交版本。
- coordination/：待办清单和模块接口约定。

## 协作方式

各自从 main 创建 feature 分支，提交后通过 Pull Request 合并。先在 coordination/interfaces.md 确认字段和接口，再并行开发。文档用 Markdown 或可编辑文件保存，最终报告另导出 PDF。

只上传合成数据；不提交密码、云密钥、真实个人数据、本地数据库或日志。此仓库的说明用于任务组织，不是可直接提交的报告正文；提交内容由成员独立完成并遵循课程要求。
