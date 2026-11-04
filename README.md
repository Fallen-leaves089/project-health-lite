# Project Health Lite

[English](#project-health-lite) | [中文](#项目体检轻量版)

A lightweight, read-only project checkup skill for people who are not full-time developers or security specialists. It gives a plain-language answer to three questions:

- Is this project ready to ship?
- What should I check before handing it over?
- Can I trust what an AI agent just changed?

**Who it's for**: no coding, Git, CI, or security background is required. If you can use an agent, you can ask in plain language.

The skill supports pre-launch, handover, and agent-change acceptance modes. Findings are grouped into **blocks launch**, **fix before delivery**, and **can wait**.

This is an independent lite edition, not a replacement for the professional [`project-health`](https://github.com/Fallen-leaves089/project-health). The lite edition focuses on first-pass checks and accessibility; the professional edition covers deeper audits, enterprise rule packs, and support.

**Which edition**: use this lite edition as the default for everyday users and first-pass checks. Escalate to `project-health` for deep audits, P0-P3 findings, evidence chains, real regression, or delivery acceptance.

## Install

Copy the whole `project-health-lite/` directory into your host's skills directory:

| Host | Common location |
|---|---|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| Other Agent Skills hosts | Follow the host documentation |

`SKILL.md` must be at the root of the installed skill folder. The folder also contains `AGENTS.md` and `PITFALLS.md`; keep them so the agent can apply standing rules and accumulate lessons. No account, network access, or configuration is required.

## Usage

In a project directory, ask:

```text
Is this project ready to ship?
```

You can also ask:

```text
Check this before handover.
An AI agent just changed this; help me verify it.
```

The first pass is read-only. The agent must ask for explicit approval before running tests, builds, installs, or other commands that may write files.

It also confirms the scope: an agent-change acceptance starts with the current diff, while launch and handover checks default to the whole project. A project without Git can still be checked from a read-only snapshot, but the report must say that change history is unavailable.

## Output

Reports use three plain-language categories:

- Blocks launch
- Fix before delivery
- Can wait

Every finding includes a file location, the reason it matters, and the next step. Evidence is marked as **verified**, **inferred**, or **not checked** so conclusions do not sound more certain than they are. Every report ends with the parts that were not checked. See [references/report-format.md](references/report-format.md) for the full format.

## Safety boundaries

- Read-only by default
- No automatic edits, deletions, deployments, releases, or migrations
- Never displays secrets, tokens, cookies, private keys, or production credentials
- Does not read `.ssh`, browser profiles, or password managers
- Never turns "not found" into "absolutely safe"

## Getting better with use

The skill folder includes `AGENTS.md` and `PITFALLS.md`. The agent reads the pitfalls log before each task and records new pitfalls in it. It searches for an existing entry first; a duplicate pitfall updates that entry instead of creating a synonym. Checks of other projects remain read-only: write the entry back to the skill folder, or ask before writing to the target project.

## License

Apache-2.0. Individuals and companies may use, modify, and distribute it, provided the license and NOTICE are retained.

## Status

`0.1.4`: routing with the professional edition and a "three actions first" report header. Real model behavior tests, sample projects, and a one-click installer are not included yet.

---

# 项目体检·轻量版

[English](#project-health-lite) | 中文

给普通人的低门槛项目体检。它用一份说人话的报告回答：

- 这个项目现在能不能上线？
- 交接前最该看什么？
- Agent 改完代码，能不能信？

**适合谁**：不需要懂代码、Git、CI 或安全术语；只要能使用 Agent，就可以用日常语言发起检查。

这是独立的轻量版，不是专业版 [`project-health`](https://github.com/Fallen-leaves089/project-health) 的替代品。轻量版负责第一次体检和普及，专业版负责深度检查、企业规则包和审计服务。

**怎么选**：普通用户和第一次体检默认用本技能；需要深度审计、P0-P3、证据链、真实构建/迁移/容器回归或交付验收时，升级专业版。

## 安装

把整个 `project-health-lite/` 目录复制到宿主的 skills 目录：

| 宿主 | 常见目录 |
|---|---|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| 其他 Agent Skills 宿主 | 以宿主文档为准 |

安装后目录根部必须有 `SKILL.md`。目录里的 `AGENTS.md` 和 `PITFALLS.md` 也要一起保留，Agent 才能应用常驻规则并积累避坑经验。不需要账号，不需要联网，不需要配置。

## 第一次使用

在项目目录里说：

```text
帮我看看这个项目能不能上线
```

也可以说：

```text
交接前帮我检查一下
Agent 刚改完，帮我验收
```

第一次只做只读检查；需要运行测试、构建或安装依赖时，Agent 会先请求同意。

Agent 验收默认先看本次改动；上线和交接默认看整个项目。没有 Git 的项目仍可做只读快照检查，但报告会说明看不到变更历史。

## 输出

报告分三档，不使用 P0/P1 作为主分类：

- 会卡住上线
- 最好先修
- 可以以后再说

每条都带文件位置、原因和下一步。证据会标成 **已验证**、**推断** 或 **未检查**，避免把不确定写成确定。报告最后会写明没检查到的部分。完整格式见 [references/report-format.md](references/report-format.md)。

## 安全边界

- 检查阶段默认只读
- 不自动修改、删除、部署、发布或迁移
- 不展示密钥、令牌、Cookie、私钥或生产凭据
- 不读取 `.ssh`、浏览器配置和密码管理器
- 不把“没发现”写成“绝对安全”

## 越用越强

技能目录里有 `AGENTS.md` 和 `PITFALLS.md`。每次任务先读避坑记录；遇到新的坑就写入，先查重，重复的坑只补充原条目。检查别人的项目时保持只读，避坑记录写回技能目录，或先取得同意再写目标项目。

## 产品定义

目标用户、三种模式、非目标和验收标准见 [docs/PRODUCT.md](docs/PRODUCT.md)。

## 许可证

Apache-2.0。个人和企业都可以免费使用、修改和分发，保留许可证与 NOTICE 即可。

## 当前状态

`0.1.4`：新增与专业版的路由规则，以及“先做这三件事”的报告开头。还没有接入真实行为测试、示例项目和一键安装包。
