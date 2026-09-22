# Campus Job Application Workflow · AI 驱动的秋招投递工作流

> 把秋招网申交给 AI Agent，把时间留给判断。
> An AI-driven workflow that automates campus recruitment applications — queue state machine, budget rules, a six-check pre-submit protocol, per-company playbooks, and human-AI handoff for CAPTCHAs.

## 背景 Background

秋招投递是典型的"高重复、强规则、多陷阱"流程：每家公司的网申系统不同、验证码各异、志愿规则各异，人工投递耗时且易错。本项目把整套流程抽象成**流程通用、数据私有**的三层架构，让 AI 在明确规则与安全红线内完成登录以外的一切，人只处理必须本人的环节（滑块/人脸/扫码/最后提交）。

In campus recruiting, applying is high-volume, rule-heavy, and full of per-company traps. This project abstracts the whole pipeline so an AI agent can do everything except what legally/physically requires the human — with strict budget rules and a no-fabrication red line.

## 核心设计 Core Design

**三层架构（流程通用、数据私有）**

```
┌─────────────────────────────────────────────┐
│ 流程层（通用核心）                            │
│  · 状态机队列 ready / blocked / submitted     │
│  · 每轮预算：≤3家/30min，同失败≤2次新依据     │
│  · 提交前六查：岗位城市毕业窗口/字段真实来源/  │
│    共享历史去重/志愿额度/特殊声明/真实附件     │
│  · 证据纪律：仅官方明确成功+岗位名一致才算提交 │
├─────────────────────────────────────────────┤
│ 公司攻略层（半通用）                          │
│  · 每家一份 playbook：渠道URL/字段映射/已踩的坑│
│  · 跨公司通用坑库：验证码消耗/短信码5分钟过期/ │
│    滑块风控/保存失败清空编辑器/日期控件        │
├─────────────────────────────────────────────┤
│ 个人数据层（私有，永不入库）                  │
│  · 简历/证件/证明 + 网申基础信息.json         │
│  · 凭证点号文件；短信读取按签名+时间窗窄查     │
└─────────────────────────────────────────────┘
```

**人机协作是默认而非降级**：滑块/拼图/人脸无法承诺全自动。AI 保存恢复点后转人工，用户操作完 AI 接手——连续失败 ≥3 次同一环节即停止自动重试。

**成功只有官方确认一种**：登录/填表/草稿 ≠ 投递成功。必须官方页面明确成功 + 岗位名称一致 + 证据截图落盘。

## 实战成果 Results（2026 秋招）

- 用本工作流驱动无头浏览器完成 **20+ 家公司**网申流程，含多家银行总行/分行（完整双志愿提交+报名序列号留证）、香港量化与 Web3 公司实习申请
- 沉淀 **15+ 条跨公司坑**与对策（见 `playbook/跨公司通用坑.md`）
- 抽象为通用模板包（本仓库），**零个人信息**，任何求职者可复制即用

## 快速开始 Quick Start

1. 复制 `templates/网申基础信息模板.json` → 填成你自己的材料库（字段带注释，无来源不填）
2. 把 `docs/启动提示词.md` 全文发给你的 AI（Kimi / Claude / ChatGPT 均可），工作区指向本目录
3. 每轮 AI 只动 `ready` 队列；遇到需本人环节会停下并写明恢复点

环境搭建（Playwright / OCR / 短信读取 / 定时轮询）见 `docs/环境搭建说明.md`。

## 仓库结构 Layout

```
├── README.md（本文件）
├── 规则.md                  # 状态机/预算/六查/事实优先级/红线
├── docs/
│   ├── 启动提示词.md         # 发给 AI 的入口指令
│   └── 环境搭建说明.md       # macOS + Playwright
├── templates/
│   ├── application-state.json    # 队列状态机模板
│   ├── 网申基础信息模板.json      # 带字段注释的空材料库
│   └── 共享历史模板.md           # 防跨AI/跨轮重复协议
└── playbook/
    ├── _模板.md                  # 每家公司一份攻略的格式
    ├── 跨公司通用坑.md            # 验证码/滑块/会话等共性对策
    └── 参考攻略_建设银行样例.md    # 已打通样例（脱敏）
```

## 安全红线 Security & Privacy

- 本仓库为通用模板，**不含任何个人信息**（简历/证件/账号永不入库）
- 凭证只读本机点号文件，禁止写入日志/聊天记录
- 短信验证码读取需用户显式授权，按公司签名+时间窗窄查，只取验证码
- 身份证号、亲属信息仅存本地，对外输出一律脱敏

## License

MIT（模板与文档可自由复用；使用者对自己的填报内容负责）
