# C3 数据处理

负责人：Member 3。

任务范围：Table 2 手算；至少 30 条合成记录的清洗统计与核对；partitions、Spark 与 MapReduce、单机局限和实际规模分析。链接 processing/、data/ 和 evidence/C3/。

本目录放章节工作材料、表格和说明；不要把此任务说明作为报告正文。

## C-II 工作材料

- [Table 2 逐步推演](hand-trace.md)：排除记录、map、shuffle、reduce 与总数。
- [40 条扩展数据的预期核对](reference-count.md)：30 个有效唯一响应，Good/OK/Poor 为 12/10/8。
- [技术说明与反思](report.md)：partitions、Spark/MapReduce、单机限制、实际规模。
- [要求核对表](requirements-checklist.md)、[C3 官方引用](sources.md)。
- [执行说明](../../processing/spark/README.md)、[真实执行证据](../../evidence/C3/README.md)。
- [8 页 PDF 工作材料](c3-working-notes.pdf)：结果说明、推演表、完整行级审计、执行信息、引用和程序附录。

PDF 可在完成数据验证后重新构建（可选排版依赖，不影响 Spark 执行）：

```powershell
.venv/c3-runtime/Scripts/python.exe -m pip install reportlab==4.4.9
.venv/c3-runtime/Scripts/python.exe docs/C3-data-processing/build_notes.py
```

C3 的 PySpark 3.5.7 版本与 Member2 最新 B-II 方案保持一致，未改写其文件。

课程 PDF 第 2 页禁止 AI 生成的提交材料。这些文件属于 AI 辅助工程工作材料，
不宣称学生独立撰写、亲自手算或已获得课程许可；正式提交需遵守该限制。
本次仅维护 C3 目录，未修改共享引用总表、其他成员章节或 A3。
