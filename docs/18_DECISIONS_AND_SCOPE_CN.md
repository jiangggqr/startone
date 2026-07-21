# 18 最终决策与冲突解决

如果文件之间出现冲突，优先级如下：

1. 本文件
2. `AGENTS.md`
3. `STARTFRAME_FULL_SPEC_CN.md`
4. 编号较高且更具体的相关规格
5. 低保真原型
6. 旧提交记录

## 已确认决策

### 产品形态

Web App 内包含一个适应性学习规划 Agent 和一个情境化 Tutor。

### 主要内容来源

用户上传材料。仅输入主题是备用模式，必须标记为 AI 生成。

### Agent 与 Tutor

- Tutor 教当前概念
- Guided Mastery Loop 出题、评估、鼓励和补救
- Agent 只决定一个全局下一步
- 学习适应判断只能来自经过服务端验证的 `LearningEvidence`
- 当前路线、剩余时间、精力、前置关系、来源覆盖和重试次数只作为约束输入，不能替代学习证据
- Feedback 的 `next_micro_action` 只允许在当前 Guided Mastery Loop 内选择一次局部练习；不得改变概念、路线、触发搜索或结束会话

### LearningEvidence

只包含事实和观察，不包含推荐。

- `activity_type` 枚举为 `tutor_check | quiz | recall | remedial`
- Tutor 不为每条消息创建 Evidence；在一次检查问题完成、用户明确表示仍困惑，或 Tutor 会话关闭时聚合一条事实记录
- `source_gap_signal` 只描述“材料没有覆盖某个已命名内容”的观察，不等于 `search_needed`

### 网络搜索

统一称为“四重搜索门”，四项必须同时满足：

1. 会话设置允许系统建议搜索
2. 存在服务端验证的命名 `SourceGap`
3. Agent 唯一动作是 `request_search`
4. 用户确认本次搜索的目标与范围

服务端只在四重门全部通过后的执行端点中向 Responses API 提供 `web_search` 工具，并要求本次调用执行搜索。拒绝或失败不终止会话，不自动重复搜索。

### 用户控制

Agent 只有一个主推荐，但用户可以覆盖。暂停、提示、重试和结束不视为失败。

用户覆盖时只显示当前状态允许的替代动作；无命名缺口时不得提供搜索，无可验证前置关系时不得提供插入前置知识。

### 用户与数据隔离

MVP 不实现账户系统。每个浏览器首次访问时获得一个随机、不可猜测的匿名 workspace ID，保存于安全的同站 Cookie；服务端所有会话、来源、导出和删除操作都按 workspace ID 隔离。Demo fixture 为只读公共模板，用户开始 Demo 后复制到自己的 workspace。

本地开发默认只监听 `127.0.0.1`。公开部署必须使用 HTTPS、安全 Cookie、请求体限制和每 workspace 配额。

### 文件保存、复制、导出与删除

- 原始上传文件保存在 `instance/uploads/{workspace_id}/`，使用服务端 UUID 文件名；用户文件名只作为元数据
- SQLite 保存来源、定位、状态和审计元数据；原始材料和完整自由文本不得写入普通日志
- 相同内容以 checksum 对应不可变 blob；复制会话复制会话与来源关联，允许共享 blob，不复制物理文件
- 删除来源只删除该会话关联；无其他关联时删除 blob
- 删除会话级联删除活动、尝试、Evidence、决策、搜索请求和该会话独占来源
- “删除全部数据”删除该 workspace 的所有数据库记录、上传 blob 和本地草稿；不可恢复
- 导出提供一个 JSON 完整记录和一个 Markdown 人类可读总结，不包含服务端密钥、隐藏推理或内部 Prompt

### ADHD 表述

使用 ADHD-informed，不做医学诊断、治疗或神经机制保证。

### 产品界面与提交语言

生产 Web App 中所有用户可见内容统一使用英文，包括导航、按钮、表单、来源标签、状态、错误、恢复提示、Demo fixture、Tutor、练习、反馈、Agent 理由、搜索确认和数据控制。中文只用于内部产品规格与开发说明，不得出现在运行中的产品界面。Devpost 文案、README、演示视频音频或字幕也使用英文。

### 视觉风格

产品界面使用纯色背景、清晰边界和克制阴影建立层级，不使用大面积渐变背景。模态框背景只做均匀遮罩，不使用渐变或大范围模糊效果。

### 技术栈

Python 3.11+、FastAPI、Uvicorn、SQLite、静态 HTML/CSS/JS。除非记录新决策，不使用 Node 构建系统。

### OpenAI

使用 GPT-5.6 与 Responses API。固定 UI 数据使用 Structured Outputs；Agent 使用受控工具/function calling；搜索使用 web search。

- Milestone 0–1 不调用模型
- Milestone 2 首次建立真实 GPT-5.6 Structured Outputs 路径，用于来源覆盖、知识地图和启动动作，同时保留确定性 Demo 路径
- Milestone 4–6 复用同一服务端 AI gateway 实现 Tutor、练习、反馈、Agent 和搜索
- 模型名通过配置提供，默认 `gpt-5.6`；真实模式无 Key 时必须明确失败，不得降级成未标记 Demo
- `OPENAI_API_KEY` 只由开发者在本地或部署环境的 `.env`/secret 配置中提供，不通过聊天传递，不写入客户端、日志、文档或 Git 提交

### 来源类型与定位

用户界面来源类型固定为 `uploaded | external | ai_supplement`。`pasted` 是 `SourceDocument.media_kind`，在 UI 中映射为 `uploaded`。

- PDF 定位：页码、页内片段序号、页内字符范围
- Markdown/TXT 定位：标题路径、开始/结束行、文档字符范围
- 粘贴文本定位：标题、段落序号、文档字符范围
- 外部来源定位：规范 URL、发布者、访问时间、引用片段和网页内定位（可获得时）
- AI 补充解释没有虚假页码或行号，必须带生成说明和它所依据的已验证来源引用（如有）

### Demo 基线

默认稳定 Demo 使用两份用户材料：`transformer_notes.md` 和 `matrix_prerequisite.md`。主路线固定为：Transformer 目标 → Self-attention → Q/K/V → Scaled dot-product attention → Positional information；Weighted sum 是 Self-attention 的掌握要点，不单独占用主路线概念。

受控搜索 Demo 使用单独场景，只导入 `transformer_notes.md`，因此矩阵/点积前置解释成为命名缺口。低保真原型和 Demo 文案统一使用 Markdown 标题与行号；PDF 页码仅在独立 PDF 解析验收 fixture 中展示。

### 状态与恢复

暂停是覆盖在当前业务状态之上的可恢复状态，不是线性流程末端。服务端保存 `resume_state`、当前概念、活动、草稿版本、提示深度和计时状态；恢复时回到这些字段描述的位置。

客户端草稿采用 `version` 做乐观并发控制。冲突时保留本地与服务端两个版本，必须由用户选择合并/保留，禁止静默覆盖。

Milestone 3 进一步固定以下实现决定：

- Demo 路线中的“Transformer 目标”作为方向说明在进入专注工作区时记为已完成，首个主动学习概念是 `Self-attention`；其他路线默认从确认路线的第一个概念开始
- 启动回答与专注笔记是可恢复草稿，不是 `LearningEvidence`，不得触发 Agent 决策
- 暂停时冻结计时并阻止学习写操作；恢复后从相同业务状态继续，暂停本身不创建失败或能力判断
- “保存并退出”先完成服务端同步和暂停，再显示当前概念、专注笔记和一个具体下次启动动作

### Tutor 会话

- 每个 session/concept 组合保留一个 Tutor thread；关闭与重新打开不删除历史，刷新从相同消息与未发送草稿恢复
- Tutor 仍是 `learning_concept` 上的界面状态，不改变全局主状态、概念顺序或路线
- Tutor 输出使用严格 `TutorResponseOutput`，来源引用保存前按 workspace、session、source、chunk 验证
- 上传材料中的说明显示 `uploaded`；不在材料中的示例必须显示 `ai_supplement`，但仍携带它所依据的已验证来源引用
- 真实 Tutor 调用不提供任何工具，尤其不提供搜索；只选取当前概念来源和与本次问题匹配的少量片段，不默认发送全部材料
- Tutor 消息可记录事实性的 `confusion_signal` 与 `prerequisite_gap_signal`；关闭时只记录信号数量。`LearningEvidence` 在 Milestone 4C 的检查边界统一生成，当前阶段不按消息制造 Evidence

### Quiz 与自由复述活动

- 新练习只能从未暂停的 `learning_concept` 创建；创建后会话进入 `practicing`，并把实际活动 ID 保存为 `active_activity_id`
- Quiz 正确答案、各选项误解标签和选项解释在提交前只保存在服务端；自由复述的预期要点、可接受改写和误解模式同样不发送给客户端
- 每个活动恰好有 3 级渐进提示，一次只揭示一级；答案草稿、提示深度、活动版本和会话计时可在刷新、暂停和恢复后继续
- 活动题目只引用当前概念经过验证的来源；真实模型调用使用严格 `QuizActivityOutput` 或 `RecallActivityOutput`，不提供任何工具
- Milestone 4B 的提交只持久化原始尝试、提示深度和用时，不生成 `LearningEvidence`、Agent 决策或搜索请求；这些尝试由 Milestone 4C 的统一反馈边界评估

### 备用“仅输入主题”模式

它不是评委主流程。真实模式可用 GPT-5.6 生成 AI supplemental source；Demo 模式提供明确标记的固定 AI fixture。此模式从首页视觉上弱于上传材料，并始终显示“AI 补充解释”，不能产生伪造的上传来源定位。

### 原型

`prototype/startframe_lowfi_prototype.html` 是交互和布局参考，不是生产代码。

### MVP 范围

必须完成完整闭环和生产级基础状态。不在截止前加入多 Agent、教师后台、排行榜或支付系统。
