# 贡献指南

## 原则

- 保持普通用户可用：默认零配置、默认只读、结论说人话。
- 新增检查项时，写清“为什么它会影响上线、交接或 Agent 验收”。
- 新增脚本必须带正反例：应该通过的样本要通过，应该失败的样本必须失败。
- 不提交真实密钥、客户数据、内部地址、个人绝对路径或未脱敏日志。

## 开发流程

1. 从议题或明确需求开始，先说明改什么、为什么、影响范围。
2. 修改后运行：

```bash
python scripts/verify_skill.py --self-test
python scripts/verify_skill.py
```

3. 发布前按 [tests/acceptance-cases.md](tests/acceptance-cases.md) 走一遍行为验收。
4. 提交信息使用清晰的动词，例如 `docs: clarify handover checklist`。
5. 提交时使用 `git commit -s`，表示同意 Developer Certificate of Origin 1.1：
   https://developercertificate.org/

## 不接受

- 用“绝对安全”“零风险”“全球最强”等承诺替代证据
- 检查阶段默认写文件或执行部署
- 为了展示效果而伪造案例、指标或客户
- 把商业版代码或许可限制混入本仓库
