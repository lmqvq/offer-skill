<div align="center">

# offer-skill

### *双视角求职与招聘 Skill*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Workflows: 4](https://img.shields.io/badge/Workflows-4-success.svg)](../../references/workflow-status.md)
[![Research Profiles: 3](https://img.shields.io/badge/Research-3%20profiles-blue.svg)](../../references/research-status.md)
[![Codex Skill](https://img.shields.io/badge/Skill-Codex-black.svg)](../../SKILL.md)
[![Stars](https://img.shields.io/github/stars/lmqvq/offer-skill?style=social)](https://github.com/lmqvq/offer-skill/stargazers)

[概述](#这个项目是什么) · [能力](#当前能力) · [研究模式](#研究模式) · [安装](#-安装) · [使用方式](#-使用方式) · [效果示例](#-效果示例) · [输出结果](#示例输出) · [文档](#文档)

[**English**](../../README.md) · [**中文**](README_ZH.md)

</div>

---

`offer-skill` 的目标，是让候选人和面试官围绕同一份材料工作，但站在不同视角得到不同价值。

- 候选人希望把项目讲清楚、发现简历薄弱点、准备面试、复盘表现。
- 面试官希望判断深度、识别弱证据、设计更有区分度的问题、复盘面试质量。
- 大多数 AI 工具只给一次回答，而 `offer-skill` 会把简历、JD、项目说明、面试记录沉淀成可复用的 **case 资产**。

一句话概括：

> 简历 + JD + 项目材料 + 面试记录 -> 结构化 case -> 可复用的求职招聘分析

## 这个项目是什么

`offer-skill` 不是简单的 prompt 集合。

它是一个围绕以下能力组织起来的 Skill 仓库：

- 双视角：`candidate`、`interviewer`、`dual`
- 四个工作流：
  - `project-highlight`
  - `resume-eval`
  - `mock-interview`
  - `interview-retro`
- 三种研究模式：
  - `local-only`
  - `web-assisted`
  - `deep-research`
- case 持久化：把材料和输出沉淀到 `cases/{case_slug}/`
- 确定性脚本：统一处理 case 创建、材料导入、工作流执行、备份回滚、研究结果落盘

## 它解决什么问题

### 候选人侧

- “我确实做了不少事，但项目一讲出来就很平。”
- “我不知道我的简历到底哪些地方和这个 JD 真匹配。”
- “我想要更贴合我自己材料的模拟面试，而不是泛泛题库。”
- “面试结束后，我想知道到底是不会，还是会但没讲清楚。”

### 面试官侧

- “这份简历看起来不错，但硬证据到底在哪？”
- “我需要能区分浅层熟悉和真实负责的问题。”
- “我想结构化复盘一次面试，而不是只靠印象。”
- “我希望能结合外部趋势信号，但结论仍然扎根在候选人的真实材料上。”

## 🔧 特性

- **双视角**：支持 `candidate`、`interviewer`、`dual`
- **case 化工作流**：围绕同一份简历、JD、项目说明、面试记录持续复用
- **四个工作流**：`project-highlight`、`resume-eval`、`mock-interview`、`interview-retro`
- **三种研究模式**：`local-only`、`web-assisted`、`deep-research`
- **持久化输出**：所有分析都会写回 case 目录
- **版本备份与回滚**：更新前可备份，出问题可恢复

## 当前能力

| 工作流 | 作用 | 常见输入 | 输出 |
|---|---|---|---|
| `project-highlight` | 提炼项目价值、责任边界、风险点和深挖问题 | 项目说明，可选简历/JD | 项目亮点分析 |
| `resume-eval` | 对比简历与 JD，识别弱证据并生成验证问题 | 简历、JD，可选项目材料 | 简历与岗位匹配评估 |
| `mock-interview` | 基于本地材料和可选研究信号生成模拟面试流程 | JD，可选简历/项目/研究材料 | 模拟面试方案 |
| `interview-retro` | 复盘真实或模拟面试表现并给出改进建议 | 面试记录，可选回答/JD/项目/研究材料 | 面试复盘结果 |

## 研究模式

`offer-skill` 当前支持三种 research profile：

| 模式 | 适合场景 | 输入方式 |
|---|---|---|
| `local-only` | 隐私优先、强本地 grounding | 仅用户本地文件 |
| `web-assisted` | 结合外部信号增强真实感 | 本地文件 + 外部资料或在线检索 |
| `deep-research` | 更深入的面试趋势分析 | 本地文件 + 更深层外部检索与归纳 |

参考：

- [Workflow Status](../../references/workflow-status.md)
- [Research Status](../../references/research-status.md)

---

## ⚡ 安装

如果你的 AI 宿主支持从包含 `SKILL.md` 的目录里自动发现 Skill，最简单的方式是直接让 AI 从仓库 URL 安装。

示例提示词：

```text
Install the offer-skill skill for me: https://github.com/lmqvq/offer-skill
```

如果宿主不支持 repo 驱动安装，也可以手工 clone 到 skills 目录：

```bash
git clone https://github.com/lmqvq/offer-skill.git <YOUR_SKILLS_DIR>/offer-skill
```

常见示例：

| 宿主 | 常见 skill 路径 |
|---|---|
| Codex | `~/.codex/skills/offer-skill` |
| Claude Code | `~/.claude/skills/offer-skill` |
| OpenClaw | `~/.openclaw/workspace/skills/offer-skill` |

安装完成后，通过 AI 工具按名字调用即可。

---

## 🚀 使用方式

正常用户不应该手工跑一堆脚本，而应该 **直接对 AI 工具说话**。

典型请求示例：

```text
Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

Use $offer-skill to extract project highlights from this backend project note from the interviewer perspective.

Use $offer-skill to run a mock interview for this JD using my resume and project notes.

Use $offer-skill to review these interview notes and tell me what broke down.
```

AI 工具在背后应该自动完成：

- 创建或复用 case
- 导入你提供的本地材料
- 执行对应工作流
- 将结果写入 `cases/{case_slug}/`

### AI 优先调用方式

示例：

```text
Use $offer-skill to evaluate this resume against the attached JD from the interviewer perspective.

Use $offer-skill to extract project highlights from this project description for a backend engineer role.

Use $offer-skill to create a mock interview from this JD with deep-research enabled.
```

### 一次调用统一入口

仓库内部推荐通过一个统一入口脚本执行：

```bash
python scripts/offer_skill.py --workflow <project-highlight|resume-eval|mock-interview|interview-retro> ...
```

这个统一入口可以：

- 创建或复用 case
- 导入本地材料
- 执行指定工作流
- 将结果回写到 case
- 在需要时接入研究材料或在线研究

示例：

```bash
python scripts/offer_skill.py \
  --workflow mock-interview \
  --perspective candidate \
  --display-name "Backend Mock Interview" \
  --jd-file ./jd.md \
  --resume-file ./resume.md \
  --projects-file ./projects.md \
  --research-profile web-assisted \
  --research-file ./market_notes.md
```

---

## ✨ 效果示例

三个典型场景。

### 1. 候选人侧 `resume-eval`

> 输入：简历 + 后端岗位 JD

```text
User         ❯ Use $offer-skill to evaluate my resume against this JD from the candidate perspective.

offer-skill  ❯ Overall match: medium
               Strong matches:
               - Java backend development
               - Redis latency optimization with measurable results

               Weak matches:
               - Kafka appears in the skill list, but project evidence is thin

               Candidate suggestions:
               - Add one concrete Kafka project story
               - Move quantified outcomes closer to the top of the resume
```

### 2. 面试官侧 `project-highlight`

> 输入：某个项目的说明材料

```text
User         ❯ Use $offer-skill to extract project highlights from this project note from the interviewer perspective.

offer-skill  ❯ Candidate view:
               - Strong ownership signal around feed write-path refactor

               Interviewer view:
               - Good Redis signal, but cache consistency handling should be verified

               Suggested questions:
               - What was the hardest consistency tradeoff?
               - If traffic grew 10x, what would fail first?
```

### 3. 带研究信号的 `mock-interview`

> 输入：JD + 简历 + 项目材料 + 可选外部面试资料

```text
User         ❯ Use $offer-skill to create a mock interview from this JD with deep-research enabled.

offer-skill  ❯ Interview setup:
               - Perspective: candidate
               - Research profile: deep-research

               Question list:
               - How do you design cache consistency under high concurrency?
               - What tradeoffs did you make in your Redis invalidation strategy?
               - How would you scale this service if QPS increased sharply?

               Research signals:
               - cache consistency
               - distributed systems
               - Redis tradeoff questions
```

## 底层开发者调试流

如果你需要逐步调试系统，仍然可以使用底层脚本。

### 1. 创建 case

```bash
python scripts/create_case.py \
  --case-slug backend-java-social \
  --display-name "Backend Java Social App Prep" \
  --perspective candidate \
  --role-title "Backend Engineer"
```

### 2. 导入本地材料

```bash
python scripts/import_material.py --case-slug backend-java-social --material-type resume --from-file ./resume.md
python scripts/import_material.py --case-slug backend-java-social --material-type jd --from-file ./jd.md
python scripts/import_material.py --case-slug backend-java-social --material-type projects --from-file ./projects.md
python scripts/import_material.py --case-slug backend-java-social --material-type interview_notes --from-file ./interview_notes.md
python scripts/import_material.py --case-slug backend-java-social --material-type candidate_answers --from-file ./candidate_answers.md
```

### 3. 执行工作流

```bash
python scripts/run_workflow.py --case-slug backend-java-social --workflow resume-eval
python scripts/run_workflow.py --case-slug backend-java-social --workflow project-highlight
python scripts/run_workflow.py --case-slug backend-java-social --workflow mock-interview --research-profile web-assisted --research-file ./market_notes.md
python scripts/run_workflow.py --case-slug backend-java-social --workflow interview-retro
```

### 4. 备份与回滚

```bash
python scripts/version_manager.py --action backup --case-slug backend-java-social
python scripts/version_manager.py --action list --case-slug backend-java-social
python scripts/version_manager.py --action rollback --case-slug backend-java-social --version v1
```

## 会写出什么内容

每次分析都会落成一个可复用的 case：

```text
cases/{case_slug}/
├── meta.json
├── manifest.json
├── inputs/
├── normalized/
├── derived/
├── analyses/
├── research/
└── versions/
```

这意味着它不是“一次性聊天回复”，而是“持续可演化的分析资产”。

## 示例输出

### `resume-eval`

会产出一个 Markdown 结果，包含：

- 总体匹配度
- 强匹配项
- 弱匹配项
- 缺失证据
- 候选人补强建议
- 面试官验证问题

### `project-highlight`

会产出一个 Markdown 结果，包含：

- 项目摘要
- 候选人视角
- 面试官视角
- 证据点
- 风险点
- 建议追问
- 行动建议

### `mock-interview`

会产出一个 Markdown 结果，包含：

- 面试设置
- 分类后的问题列表
- 期待信号
- 常见失分方式
- 追问路径
- 练习计划
- 研究信号

### `interview-retro`

会产出一个 Markdown 结果，包含：

- 复盘摘要
- 哪些回答做得好
- 哪些地方出问题
- 面试官可能如何理解
- 候选人改进计划
- 下一轮练习问题

## 为什么 case 模型很重要

这个项目选择围绕 `case` 组织，是因为求职准备和面试评估天然是迭代式的。

如果没有 case 模型，你得到的往往是：

- 重复解析
- 上下文不断丢失
- 只有聊天记录，没有结构化资产

有了 case 模型，你可以得到：

- 可复用的材料
- 持久化的分析结果
- 版本备份与回滚
- 工作流之间的串联空间

## 项目结构

```text
offer-skill/
├── SKILL.md
├── README.md
├── INSTALL.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
├── presets/
├── references/
├── scripts/
├── cases/
└── tests/
```

重要目录：

- `presets/`：工作流、视角和 research profile 预设
- `references/`：scope、schema 和状态说明
- `scripts/`：内部确定性脚本
- `tests/`：工作流、case 和 research 执行相关的回归测试

## 文档

- [PRD](../PRD.md)
- [Architecture](../ARCHITECTURE.md)
- [Roadmap](../ROADMAP.md)

## 安全边界

`offer-skill` 是分析辅助工具，不是自动化招聘决策系统。

它不应该被用来：

- 伪造项目经历
- 生成欺骗性表述
- 替代人类面试官和招聘决策
- 把外部趋势信号包装成绝对正确结论

## 测试

在当前机器上，从仓库父目录运行：

```bash
python -m unittest discover -s offer-skill/tests -p "test_*.py" -v
```

## 贡献

欢迎继续增强：

- 更强的解析器
- 更真实的模拟面试生成
- 更细的面试复盘判断
- 更好的研究信号筛选与归纳
- 更自然的工作流串联

参考 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

## 致谢

这个仓库的 GitHub 展示方式，参考了 [`titanwings/colleague-skill`](https://github.com/titanwings/colleague-skill) 在 scope、install、usage、roadmap 上的呈现思路。

## License

MIT
