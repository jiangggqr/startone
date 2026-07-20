# StartFrame Agent — Codex 规格与 UI/UX 原型包 V4

本仓库是 **规格先行的开发起点**。它不包含生产应用代码，但包含 Codex 从零开发所需的完整产品、UI/UX、Agent、数据、验收和开发指令。

## 产品定义

StartFrame Agent 是一个以上传学习材料为主来源的学习 Agent Web App：

1. 用户上传 PDF、Markdown、TXT 或粘贴文本。
2. 系统保留真实页码、标题和行号，建立可核查的知识地图。
3. ADHD-informed 会话先给一个 1–2 分钟启动动作，并且一次只突出一个概念和一个主动作。
4. Contextual Tutor、Quiz、自由复述、分层提示、即时反馈、具体鼓励和补救练习组成 Guided Mastery Loop。
5. 这些活动产生 `LearningEvidence`。
6. Adaptive Planning Agent 只根据证据选择一个下一动作，不负责讲解或评分。
7. 只有会话允许、存在验证后的明确来源缺口、Agent 请求且用户确认本次搜索时，系统才使用外部搜索。

## 最先打开的文件

1. `START_HERE_CN.md`
2. `AGENTS.md`
3. `STARTFRAME_FULL_SPEC_CN.md`
4. `prototype/startframe_lowfi_prototype.html`
5. `docs/04_LOW_FIDELITY_PROTOTYPE_CN.md`
6. `docs/16_CODEX_PROMPTS_CN.md`

## UI/UX 原型

- 可点击原型：`prototype/startframe_lowfi_prototype.html`
- 全部页面总览：`prototype/startframe_lowfi_overview.png`
- 逐屏规范：`docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md`
- 组件与所有状态：`docs/06_COMPONENTS_AND_STATES_CN.md`
- 生产级 UX 标准：`docs/11_PRODUCTION_UX_STANDARDS_CN.md`

原型 HTML 是设计参考，不是生产应用架构。Codex 必须按规格重新实现，不应直接把原型代码当成最终前端。

## 当前状态

- 产品、UI/UX、Agent、数据和验收规格：已完成
- 低保真可点击原型：已完成
- 生产应用代码：未开始
- Codex 开发记录：未开始

## 如何交给 Codex

解压整个文件夹，在 Codex 中打开根目录。不要只上传 PNG，也不要逐个上传文件。Codex 会自动读取 `AGENTS.md`，并按 `START_HERE_CN.md` 与 `docs/16_CODEX_PROMPTS_CN.md` 分阶段开发。
