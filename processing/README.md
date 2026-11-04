# C3 数据处理

负责人：Member 3。选择 PySpark 本地模式或实验室 Hive；不要求两者都实现。

- spark/：PySpark 程序与对应依赖、执行说明。
- hive/：选择 Hive 时使用的 SQL 与实验室运行说明。

输入放 data/synthetic/，输出放 data/aggregated/。规则需明确：按 response ID 去重、排除非法评分并核对总数。至少 30 条合成记录，保留原始输入便于复现。
