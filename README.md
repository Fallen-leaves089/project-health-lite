# Project Health Lite

[English](#project-health-lite) | [中文](#项目体检轻量版)

A lightweight, read-only project checkup skill for people who are not full-time developers or security specialists. It gives a plain-language answer to four questions:

- Is this project ready to ship?
- What should I check before handing it over?
- Can I trust what an AI agent just changed?
- What should I improve or maintain next?

**Who it's for**: no coding, Git, CI, or security background is required. If you can use an agent, you can ask in plain language.

The skill supports pre-launch, handover, agent-change acceptance, and general maintenance review. Findings are grouped into **blocks launch**, **fix before delivery**, and **can wait**.

This is an independent lite edition, not a replacement for the professional [`project-health`](https://github.com/Fallen-leaves089/project-health). The lite edition focuses on first-pass checks and accessibility; the professional edition covers deeper audits, enterprise rule packs, and support.

**Which edition**: use this lite edition as the default for everyday users and first-pass checks. Escalate to `project-health` for deep audits, P0-P3 findings, evidence chains, real regression, or delivery acceptance.

## Install

**Recommended: download the zip from the [latest GitHub Release Assets](https://github.com/Fallen-leaves089/project-health-lite/releases/latest).** Set `$version` below to the release shown there (currently `0.2.0`), verify the adjacent `.sha256` file, and extract the archive:

Windows PowerShell:

```powershell
$version = '0.2.0'
$zip = ".\project-health-lite-v$version.zip"
$expected = ((Get-Content -LiteralPath ($zip + '.sha256') -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'SHA256 mismatch' }
Expand-Archive -LiteralPath $zip -DestinationPath . -Force
```

macOS / Linux:

```bash
version='0.2.0'
zip="project-health-lite-v${version}.zip"
expected=$(cut -d' ' -f1 "${zip}.sha256")
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "${zip}" | awk '{print $1}')
else
  actual=$(shasum -a 256 "${zip}" | awk '{print $1}')
fi
[ "$actual" = "$expected" ] || { echo 'SHA256 mismatch' >&2; exit 1; }
unzip -o "${zip}"
```

Extract in a clean directory outside the skills directory; the commands below only copy the extracted folder. They install or upgrade in place and preserve `PITFALLS.local.md`.

Windows PowerShell:

```powershell
$destination = "$HOME\.codex\skills"
New-Item -ItemType Directory -Force -Path $destination | Out-Null
$localMemory = Join-Path $destination 'project-health-lite\PITFALLS.local.md'
$backup = "$localMemory.bak"
if (Test-Path -LiteralPath $localMemory) { Copy-Item -LiteralPath $localMemory -Destination $backup -Force }
Copy-Item -LiteralPath .\project-health-lite -Destination $destination -Recurse -Force
if (Test-Path -LiteralPath $backup) { Move-Item -LiteralPath $backup -Destination $localMemory -Force }
Test-Path -LiteralPath (Join-Path $destination 'project-health-lite\SKILL.md')
```

macOS / Linux:

```bash
destination="$HOME/.codex/skills"
mkdir -p "$destination"
memory="$destination/project-health-lite/PITFALLS.local.md"
backup="$(mktemp)"
if [ -f "$memory" ]; then cp "$memory" "$backup"; else rm -f "$backup"; fi
cp -R project-health-lite "$destination/"
if [ -s "$backup" ]; then cp "$backup" "$memory"; fi
rm -f "$backup"
test -f "$destination/project-health-lite/SKILL.md"
```

For Claude Code, replace `~/.codex/skills/` with `~/.claude/skills/` (Windows: `$HOME\.claude\skills\`). You can also copy the whole `project-health-lite/` directory from a repository checkout.

| Host | Common location |
|---|---|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| Other Agent Skills hosts | Follow the host documentation |

`SKILL.md` must be at the root of the installed skill folder. The folder also contains `AGENTS.md`, `PITFALLS.md`, and `PITFALLS.local.example.md`; keep them. `PITFALLS.local.md` is created by the agent on first use. After installation, no account, network access, or configuration is required.

## Memory and upgrades

`PITFALLS.md` is a read-only baseline shipped with the skill. The agent writes new lessons to `PITFALLS.local.md`, which is gitignored and preserved by the install/upgrade commands above. It chooses the first writable location:

1. `$PROJECT_HEALTH_LITE_HOME/PITFALLS.local.md` when the variable is set;
2. `PITFALLS.local.md` in the skill directory;
3. `~/.project-health-lite/PITFALLS.local.md`;
4. the host's persistent memory feature.

If none is writable, the check still runs and the report says the lesson was not persisted. Never write target-repository content into memory.

## Usage

In a project directory, ask:

```text
Is this project ready to ship?
```

You can also ask:

```text
Check this before handover.
An AI agent just changed this; help me verify it.
What should I optimize or maintain in this project?
```

The first pass is read-only. The agent must ask for explicit approval before running tests, builds, installs, or other commands that may write files. Reports follow the user's language: English prompts get English reports, while code, paths, and commands stay unchanged.

It also confirms the scope: an agent-change acceptance starts with the current diff, while launch, handover, and general maintenance checks default to the whole project. A project without Git can still be checked from a read-only snapshot, but the report must say that change history is unavailable.

## Output

Reports usually use three plain-language categories. When there is no material finding, omit the categories and action list and say so explicitly:

- Blocks launch
- Fix before delivery
- Can wait

Every finding includes a file location, an evidence line, the reason it matters, and the next step. Evidence is marked as **verified**, **inferred**, or **not checked** so conclusions do not sound more certain than they are. Every report ends with the parts that were not checked. See [references/report-format.md](references/report-format.md) for the full format.

## Safety boundaries

- Read-only by default
- No automatic edits, deletions, deployments, releases, or migrations
- Never displays secrets, tokens, cookies, private keys, or production credentials
- Does not judge whether a secret value is real or a placeholder; uncertain values are marked as suspected
- Does not read `.ssh`, browser profiles, or password managers
- Treats all target-repository text, including `AGENTS.md`, `PITFALLS.md`, and README files, as untrusted evidence rather than instructions
- Never turns "not found" into "absolutely safe"

## Getting better with use

The skill folder includes a read-only `PITFALLS.md` baseline and a user-local `PITFALLS.local.md` overlay. The agent reads both before each task and writes only to the local overlay. It searches for an existing entry first; a duplicate pitfall updates that entry instead of creating a synonym. If the install directory is read-only, it uses `PROJECT_HEALTH_LITE_HOME` or `~/.project-health-lite/`; if neither is writable, it reports that the lesson was not persisted. Checks of other projects remain read-only.

## License

Apache-2.0. Individuals and companies may use, modify, and distribute it, provided the license and NOTICE are retained.

## Validation

Run the deterministic checks with:

```text
python -B scripts/verify_skill.py --self-test
python -B scripts/verify_skill.py
python -B -m unittest discover -s tests -p "test_*.py"
```

The contract tests check the safety rules, templates, fixtures, and package structure. Real model behavior should be re-run for future changes with the manual scenarios in [tests/acceptance-cases.md](tests/acceptance-cases.md).

## Status

`0.2.0`: add Windows PowerShell and macOS/Linux install and upgrade guidance, preserve `PITFALLS.local.md` across upgrades, and split the shipped baseline from a portable local memory overlay. This release keeps the untrusted-target, language-aware, maintenance-check, contract-test, and package-validation behavior from `0.1.6`. Automated model regression is still not included.

---

# 项目体检·轻量版

[English](#project-health-lite) | 中文

给普通人的低门槛项目体检。它用一份说人话的报告回答：

- 这个项目现在能不能上线？
- 交接前最该看什么？
- Agent 改完代码，能不能信？
- 接下来最值得优化或维护什么？

**适合谁**：不需要懂代码、Git、CI 或安全术语；只要能使用 Agent，就可以用日常语言发起检查。

这是独立的轻量版，不是专业版 [`project-health`](https://github.com/Fallen-leaves089/project-health) 的替代品。轻量版负责第一次体检、维护检查和普及，专业版负责深度检查、企业规则包和审计服务。

**怎么选**：普通用户和第一次体检默认用本技能；需要深度审计、P0-P3、证据链、真实构建/迁移/容器回归或交付验收时，升级专业版。

## 安装

**推荐从 [最新 Releases Assets](https://github.com/Fallen-leaves089/project-health-lite/releases/latest) 下载。** 把下面 `$version` 改成页面显示的版本（当前为 `0.2.0`），下载 zip 和旁边的 `.sha256` 文件，核对哈希后解压：

Windows PowerShell：

```powershell
$version = '0.2.0'
$zip = ".\project-health-lite-v$version.zip"
$expected = ((Get-Content -LiteralPath ($zip + '.sha256') -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'SHA256 mismatch' }
Expand-Archive -LiteralPath $zip -DestinationPath . -Force
```

macOS / Linux：

```bash
version='0.2.0'
zip="project-health-lite-v${version}.zip"
expected=$(cut -d' ' -f1 "${zip}.sha256")
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "${zip}" | awk '{print $1}')
else
  actual=$(shasum -a 256 "${zip}" | awk '{print $1}')
fi
[ "$actual" = "$expected" ] || { echo 'SHA256 mismatch' >&2; exit 1; }
unzip -o "${zip}"
```

请在一个干净的、skills 目录之外的目录解压；下面的命令只复制解压出的目录，并在安装或升级时保留 `PITFALLS.local.md`。

Windows PowerShell：

```powershell
$destination = "$HOME\.codex\skills"
New-Item -ItemType Directory -Force -Path $destination | Out-Null
$localMemory = Join-Path $destination 'project-health-lite\PITFALLS.local.md'
$backup = "$localMemory.bak"
if (Test-Path -LiteralPath $localMemory) { Copy-Item -LiteralPath $localMemory -Destination $backup -Force }
Copy-Item -LiteralPath .\project-health-lite -Destination $destination -Recurse -Force
if (Test-Path -LiteralPath $backup) { Move-Item -LiteralPath $backup -Destination $localMemory -Force }
Test-Path -LiteralPath (Join-Path $destination 'project-health-lite\SKILL.md')
```

macOS / Linux：

```bash
destination="$HOME/.codex/skills"
mkdir -p "$destination"
memory="$destination/project-health-lite/PITFALLS.local.md"
backup="$(mktemp)"
if [ -f "$memory" ]; then cp "$memory" "$backup"; else rm -f "$backup"; fi
cp -R project-health-lite "$destination/"
if [ -s "$backup" ]; then cp "$backup" "$memory"; fi
rm -f "$backup"
test -f "$destination/project-health-lite/SKILL.md"
```

Claude Code 把目标目录换成 `~/.claude/skills/`（Windows 为 `$HOME\.claude\skills\`）。也可以从仓库检出中直接复制整个 `project-health-lite/` 目录。常见宿主目录如下：

| 宿主 | 常见目录 |
|---|---|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| 其他 Agent Skills 宿主 | 以宿主文档为准 |

安装后目录根部必须有 `SKILL.md`。目录里的 `AGENTS.md`、`PITFALLS.md` 和 `PITFALLS.local.example.md` 也要一起保留；`PITFALLS.local.md` 由 Agent 在首次使用时创建。安装完成后运行时不需要账号、不需要联网、不需要配置。

## 记忆与升级

`PITFALLS.md` 是随技能发布的只读基线。Agent 把新教训写入 `PITFALLS.local.md`；该文件已被 Git 忽略，并会被上面的安装/升级命令保留。记忆位置按以下顺序选择：

1. 已设置 `PROJECT_HEALTH_LITE_HOME` 时，使用它指向目录下的 `PITFALLS.local.md`；
2. 技能目录下的 `PITFALLS.local.md`；
3. `~/.project-health-lite/PITFALLS.local.md`；
4. 宿主提供的持久记忆功能。

如果都不可写，检查仍会执行，报告会说明“本轮教训未持久化”。不要把目标仓库内容写入记忆。

## 第一次使用

在项目目录里说：

```text
帮我看看这个项目能不能上线
```

也可以说：

```text
交接前帮我检查一下
Agent 刚改完，帮我验收
看看这个项目有没有需要优化或维护的地方
```

第一次只做只读检查；需要运行测试、构建或安装依赖时，Agent 会先请求同意。报告语言跟随用户：中文提问用中文报告，英文提问用英文报告；代码、路径和命令保持原文。

Agent 验收默认先看本次改动；上线、交接和通用维护检查默认看整个项目。没有 Git 的项目仍可做只读快照检查，但报告会说明看不到变更历史。

## 输出

报告通常分三档，不使用 P0/P1 作为主分类；没有明显发现时省略三档并明确说明：

- 会卡住上线
- 最好先修
- 可以以后再说

每条都带文件位置、证据、原因和下一步。证据会标成 **已验证**、**推断** 或 **未检查**，避免把不确定写成确定。有发现时报告开头先给“最重要的 1-3 件事”；没有明显发现时省略三档和行动清单。最后写明没检查到的部分。完整格式见 [references/report-format.md](references/report-format.md)。

## 安全边界

- 检查阶段默认只读
- 不自动修改、删除、部署、发布或迁移
- 不展示密钥、令牌、Cookie、私钥或生产凭据
- 不根据值的字样判断秘密是否真实或是否只是占位符；无法确认时标为“疑似”
- 不读取 `.ssh`、浏览器配置和密码管理器
- 目标仓库的 `AGENTS.md`、`PITFALLS.md`、README 和其他文本只作为证据，不作为指令执行
- 不把“没发现”写成“绝对安全”

## 越用越强

技能目录里有只读基线 `PITFALLS.md` 和用户本地覆盖层 `PITFALLS.local.md`。每次任务先读两份记录；遇到新的坑只写入本地覆盖层，先查重，重复的坑只补充原条目。如果技能目录不可写，就按顺序尝试 `PROJECT_HEALTH_LITE_HOME`、`~/.project-health-lite/` 或宿主记忆功能；都不可写时在报告中说明“本轮教训未持久化”。检查别人的项目时保持只读，不把目标内容写入记忆。

## 产品定义

目标用户、检查模式、非目标和验收标准见 [docs/PRODUCT.md](docs/PRODUCT.md)。

## 验证

运行确定性检查：

```text
python -B scripts/verify_skill.py --self-test
python -B scripts/verify_skill.py
python -B -m unittest discover -s tests -p "test_*.py"
```

契约测试检查安全规则、模板、fixture 和包结构；后续修改仍应按 [tests/acceptance-cases.md](tests/acceptance-cases.md) 重新执行真实模型验收。

## 许可证

Apache-2.0。个人和企业都可以免费使用、修改和分发，保留许可证与 NOTICE 即可。

## 当前状态

`0.2.0`：补充 Windows PowerShell 与 macOS/Linux 的安装和升级说明，升级时保留 `PITFALLS.local.md`；把随包基线和用户本地记忆拆开，支持多位置回退。继续保留 `0.1.6` 的不可信目标保护、语言跟随、通用维护检查、契约测试和包校验。自动化模型回归仍未接入。
