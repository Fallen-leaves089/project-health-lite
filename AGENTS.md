# AGENTS.md — 项目体检轻量版常驻规则

本文件适用于维护本仓库、修改本技能，以及在检查任务中使用本技能的 Agent。`SKILL.md` 负责一次检查怎么做；本文件负责每次都不能破的底线。用户明确指令、安全要求和 Apache-2.0 许可优先。

## 每次任务先做

1. 先读 `PITFALLS.md` 中与当前任务、环境或工具相关的条目；命中就按“正确做法”执行。
2. 先确认任务类型：检查、计划、修改、发布。不要把“帮我看看”自动升级成“帮我修”。
3. 检查阶段默认只读：不改源码、配置、依赖和 Git 历史；不删除、移动、部署、发布、迁移数据库。
4. 写报告前先说明保存位置；运行测试、构建、安装依赖、启动服务或联网前，先说明影响并取得同意。
5. 修改任务先说明改什么、为什么改、影响范围和验证方式；未确认前不动手。

## 普通人与证据

- 默认用日常语言；第一次出现 Git、CI、迁移等术语时解释。
- 结论必须带文件位置或只读命令证据；推断标为“推断”，未检查标为“未检查”。
- 报告必须写“没检查到的部分”，不把“本轮没发现”写成“绝对安全”。

## 避坑记录

- 遇到坑就记录到 `PITFALLS.md`；先检索是否已有同类条目，重复的坑不新增同义条目。
- 重复坑需要补充时，只在原条目补充日期、适用范围或验证证据，不新开同义条目。
- 不删除旧条目；过时条目标 `[已过时]` 并说明原因。
- 同一个坑出现两次以上，提升为 `AGENTS.md` 规则、校验脚本或验收用例，不能只留在日志里。
- 检查别人的项目时保持只读：避坑条目写回本技能目录，或先取得同意再写目标项目。
- 不写密钥、令牌、个人绝对路径、客户数据或未脱敏日志。

## 项目边界

- 本仓库是 `project-health-lite` 轻量版，许可为 Apache-2.0；个人和企业均可商用，但必须保留许可证与 `NOTICE`。
- 不要把专业版 `project-health` 的 PolyForm Noncommercial 条款混进本仓库。
- 轻量版负责第一次体检和说人话的输出，不替代专业安全审计，也不替代专业版。

## English summary

- Read `PITFALLS.md` at task start.
- Review is read-only; do not edit source, configuration, dependencies, or Git history.
- Explain report paths; obtain consent before tests, builds, installs, services, or network access.
- Record every pitfall, except duplicates; update the existing entry instead.
- Apache-2.0 allows personal and commercial use; retain the license and NOTICE.
