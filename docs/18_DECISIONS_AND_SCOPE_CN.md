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

用户上传或粘贴的材料是唯一学习入口和主要来源。不提供“仅输入主题”生成学习内容的产品路径。

### 自动学习准备与基础判断

- 不显示目标、已有基础、可用时间或精力的前置表单；这些字段会增加开始前的决策成本
- AI 从材料中识别核心概念，选择一个可解释的学习重点，并生成知识框架、依赖与短路线
- AI 不得仅凭材料推断或宣称用户已经掌握什么；首次 60–120 秒回答只作为校准支持的初始信号
- Tutor 对话、Quiz、自由复述、提示使用和补救结果形成后续 `LearningEvidence`，系统再据此调整难度和路线
- 会话时长使用产品内部的紧凑默认值并允许随时暂停；可访问性、时间显示和搜索建议属于可选 Settings，不阻塞开始

### Agent 与 Tutor

- Tutor 教当前概念
- Guided Mastery Loop 出题、评估、鼓励和补救
- Agent 只决定一个全局下一步
- 学习适应判断只能来自经过服务端验证的 `LearningEvidence`
- 当前路线、剩余会话时间、前置关系、来源覆盖和重试次数只作为约束输入，不能替代学习证据
- Feedback 的 `next_micro_action` 只允许在当前 Guided Mastery Loop 内选择一次局部练习；不得改变概念、路线、触发搜索或结束会话

### LearningEvidence

只包含事实和观察，不包含推荐。

- `activity_type` 枚举为 `tutor_check | quiz | recall | remedial`
- Tutor 不为每条消息创建 Evidence；在一次检查问题完成、用户明确表示仍困惑，或 Tutor 会话关闭时聚合一条事实记录
- `source_gap_signal` 只描述“材料没有覆盖某个已命名内容”的观察，不等于 `search_needed`

### 网络搜索

统一称为“四重搜索门”，四项必须同时满足：

1. 用户未关闭受控搜索建议；该偏好只允许 Agent 提出请求，不授权执行
2. 存在服务端验证的命名 `SourceGap`
3. Agent 唯一动作是 `request_search`
4. 用户确认本次搜索的目标与范围

服务端只在四重门全部通过后的执行端点中向 Responses API 提供 `web_search` 工具，并要求本次调用执行搜索。拒绝或失败不终止会话，不自动重复搜索。

### 用户控制

Agent 只有一个主推荐，但用户可以覆盖。暂停、提示、重试和结束不视为失败。

用户覆盖时只显示当前状态允许的替代动作；无命名缺口时不得提供搜索，无可验证前置关系时不得提供插入前置知识。

### 用户与数据隔离

MVP 不实现账户系统。每个浏览器首次访问时获得一个随机、不可猜测的匿名 workspace ID，保存于安全的同站 Cookie；服务端所有会话、来源、导出和删除操作都按 workspace ID 隔离。Demo fixture 为只读公共模板，用户开始 Demo 后复制到自己的 workspace。

本地开发默认只监听 `127.0.0.1`。公开部署必须使用 HTTPS、安全 Cookie、请求体限制和每 workspace 配额。发布默认上限固定为每个 workspace 20 个会话、50 个来源；只能通过服务端环境变量调整，客户端不得覆盖。

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

生产 Web App 中所有用户可见内容统一使用英文，包括导航、按钮、来源标签、状态、错误、恢复提示、Tutor、练习、反馈、Agent 理由、搜索确认和数据控制。中文只用于内部产品规格与开发说明，不得出现在运行中的产品界面。Devpost 文案、README、演示视频音频或字幕也使用英文。

### 视觉风格

产品界面使用纯色背景、清晰边界和克制阴影建立层级，不使用大面积渐变背景。模态框背景只做均匀遮罩，不使用渐变或大范围模糊效果。

### 技术栈

Python 3.11+、FastAPI、Uvicorn、SQLite、静态 HTML/CSS/JS。除非记录新决策，不使用 Node 构建系统。

### OpenAI

使用 GPT-5.6 与 Responses API。固定 UI 数据使用 Structured Outputs；Agent 使用受控工具/function calling；搜索使用 web search。

- Milestone 0–1 不调用模型
- Milestone 2 首次建立真实 GPT-5.6 Structured Outputs 路径，用于来源覆盖、知识地图和启动动作，同时保留确定性 Demo 路径
- Milestone 4–6 复用同一服务端 AI gateway 实现 Tutor、练习、反馈、Agent 和搜索
- 模型名通过配置提供，默认使用适合交互延迟的 GPT-5.6 系列模型 `gpt-5.6-luna`；真实模式无 Key 时必须明确失败，不得降级成未标记 Demo
- `OPENAI_API_KEY` 只由开发者在本地或部署环境的 `.env`/secret 配置中提供，不通过聊天传递，不写入客户端、日志、文档或 Git 提交

### 来源类型与定位

用户界面来源类型固定为 `uploaded | external | ai_supplement`。`pasted` 是 `SourceDocument.media_kind`，在 UI 中映射为 `uploaded`。

- PDF 定位：页码、页内片段序号、页内字符范围
- Markdown/TXT 定位：标题路径、开始/结束行、文档字符范围
- 粘贴文本定位：标题、段落序号、文档字符范围
- 外部来源定位：规范 URL、发布者、访问时间、引用片段和网页内定位（可获得时）
- AI 补充解释没有虚假页码或行号，必须带生成说明和它所依据的已验证来源引用（如有）

### 内部确定性验收基线

内部确定性验收使用两份材料：`transformer_notes.md` 和 `matrix_prerequisite.md`。主路线固定为：Transformer 目标 → Self-attention → Q/K/V → Scaled dot-product attention → Positional information；Weighted sum 是 Self-attention 的掌握要点，不单独占用主路线概念。

受控搜索验收夹具使用单独场景，只导入 `transformer_notes.md`，因此矩阵/点积前置解释成为命名缺口。低保真原型统一使用 Markdown 标题与行号；PDF 页码仅在独立 PDF 解析验收 fixture 中展示。

确定性夹具、受控搜索测试和运行模式只用于自动化或本地验收，不进入最终学习界面。真实产品由服务端 GPT-5.6 分析用户上传的材料；不得用固定结果处理任意公开上传。

### 首页、上传与设置的信息层级

- 上传成功后必须在上传面板内显示逐文件名称、解析状态、来源类型和操作，顶部状态条只承担补充反馈，不能成为唯一确认
- 至少一份材料就绪后显示一个主下一步：生成学习路线；页面同时说明 AI 将识别重点、建立概念路线并用首次短回答校准支持
- 首页只保留产品价值、上传主入口和学习记录，不放大块数据治理、系统边界、API 状态或评审测试说明
- 导出、AI 活动、学习/无障碍偏好与删除全部数据进入 `Settings`；系统边界在来源标签、Agent 决策和搜索确认等相关时刻按上下文展示

### 状态与恢复

暂停是覆盖在当前业务状态之上的可恢复状态，不是线性流程末端。服务端保存 `resume_state`、当前概念、活动、草稿版本、提示深度和计时状态；恢复时回到这些字段描述的位置。

客户端草稿采用 `version` 做乐观并发控制。冲突时保留本地与服务端两个版本，必须由用户选择合并/保留，禁止静默覆盖。

Milestone 3 进一步固定以下实现决定：

- 内部验收路线中的“Transformer 目标”作为方向说明在进入专注工作区时记为已完成，首个主动学习概念是 `Self-attention`；真实路线默认从确认路线的第一个概念开始
- 启动回答与专注笔记是可恢复草稿，不是 `LearningEvidence`，不得触发 Agent 决策
- 暂停时冻结计时并阻止学习写操作；恢复后从相同业务状态继续，暂停本身不创建失败或能力判断
- “保存并退出”先完成服务端同步和暂停，再显示当前概念、专注笔记和一个具体下次启动动作

### Tutor 会话

- 每个 session/concept 组合保留一个 Tutor thread；关闭与重新打开不删除历史，刷新从相同消息与未发送草稿恢复
- Tutor 仍是 `learning_concept` 上的界面状态，不改变全局主状态、概念顺序或路线
- Tutor 输出使用严格 `TutorResponseOutput`，来源引用保存前按 workspace、session、source、chunk 验证
- 上传材料中的说明显示 `uploaded`；不在材料中的示例必须显示 `ai_supplement`，但仍携带它所依据的已验证来源引用
- 真实 Tutor 调用不提供任何工具，尤其不提供搜索；只选取当前概念来源和与本次问题匹配的少量片段，不默认发送全部材料
- Tutor 消息可记录事实性的 `confusion_signal` 与 `prerequisite_gap_signal`；不按每条消息制造 Evidence。Milestone 4C 在 Tutor 关闭边界仅聚合关闭以来的新 Tutor 输出，生成一条 `activity_type=tutor_check`、`outcome=unresolved` 的事实记录，不把未评分对话误报为掌握或失败

### Quiz 与自由复述活动

- 新练习只能从未暂停的 `learning_concept` 创建；创建后会话进入 `practicing`，并把实际活动 ID 保存为 `active_activity_id`
- Quiz 正确答案、各选项误解标签和选项解释在提交前只保存在服务端；自由复述的预期要点、可接受改写和误解模式同样不发送给客户端
- 每个活动恰好有 3 级渐进提示，一次只揭示一级；答案草稿、提示深度、活动版本和会话计时可在刷新、暂停和恢复后继续
- 活动题目只引用当前概念经过验证的来源；真实模型调用使用严格 `QuizActivityOutput` 或 `RecallActivityOutput`，不提供任何工具
- Milestone 4B 的提交只持久化原始尝试、提示深度和用时，不生成 `LearningEvidence`、Agent 决策或搜索请求；这些尝试由 Milestone 4C 的统一反馈边界评估

### Feedback、补救与 LearningEvidence

- 每个已提交的 Quiz、自由复述或补救尝试由独立反馈边界评估；反馈固定显示已掌握、缺失/不清楚、简短纠正、具体鼓励和一个当前概念内微动作
- Feedback 的 `next_micro_action` 只用于当前 Guided Mastery Loop，不进入 `LearningEvidence`，也不代表 Agent 的全局下一步动作
- `LearningEvidence.outcome` 固定为 `mastered | partial | needs_support | unresolved`；其中 `unresolved` 用于未经评分的 Tutor 检查边界
- `LearningEvidence` 数据表和公开结构只保存活动类型、概念、结果、要点覆盖、误解标签、提示深度、用时、Tutor 困惑信号、补救结果、来源缺口信号和时间；明确不设 `next_action`、`recommendation`、`should_continue` 或 `search_needed` 字段
- 补救策略固定为 `simpler_explanation | smaller_question | concrete_example | contrast_question | rephrase_task`，只针对最近一次具体缺口；系统按已用策略切换形式，不连续重复同一策略
- 反馈生成后会话进入 `feedback_shown`；可选补救进入 `remedial_practice`；用户完成反馈边界后进入 `evidence_ready`。三个状态都支持暂停和精确恢复
- Milestone 4C 不创建 Agent 决策，不提供搜索工具，也不执行外部搜索；`evidence_ready` 只表示下一阶段可以由 Agent 读取证据

### 受控外部搜索

- 搜索请求必须绑定当前 session、concept、已验证 `SourceGap` 与已接受或覆盖选择的 `request_search` Agent decision；不能由 Tutor、反馈或客户端自由创建范围
- 确认页先显示命名缺口、建议范围、用户可读理由和四项门状态，并明确显示 `No search has run`；用户拒绝后直接回到当前概念且不生成外部来源
- 执行端点再次检查四项门、session/request 乐观版本与 workspace 所有权；失败只保存可恢复错误，不自动重试，不终止学习会话
- 真实模式向 Responses API 提供唯一 `web_search` 工具并设置 `tool_choice=required`；保存前只接受最终回答 `url_citation` 标注中的公共 HTTPS URL，工具咨询但未引用的来源不进入结果，URL 移除 fragment 并拒绝 localhost/私网直接地址
- 外部结果只保留小集合，展示规范 URL、标题、发布者、访问时间、cited summary、选择理由和 `external` 标签；用户最多选择一个连接到当前概念，也可以无惩罚忽略
- 选择外部补充后，focus payload 继续把上传材料声明为 `primary_origin=uploaded`，外部材料单列为 supplement，不改变原材料的来源身份
- 内部确定性搜索测试不调用互联网并使用固定 cited results；该夹具通过自动化测试或开发 API 验证，不在 `Help` 或其他学习界面中暴露评审入口

### 无材料主题模式

明确不做。若用户没有上传或粘贴材料，界面保持材料空状态，不让 GPT-5.6 凭主题生成一条替代学习路线。

### 原型

`prototype/startframe_lowfi_prototype.html` 是交互和布局参考，不是生产代码。

### MVP 范围

学科定位采用 **AI-first, not AI-only**。首发市场和演示内容优先使用 AI 论文、课程讲义和技术文档，但生产流程不拒绝其他有清晰文字材料的学科。当前核心差异是专注友好的启动、知识结构、Guided Mastery Loop、来源核查和证据驱动推进，而不是 AI 学科专属内容引擎。在代码执行与调试、公式/架构图理解、AI 先修知识图谱、技术时效检查和专项评测完成前，不在产品界面承诺“只为 AI 学习”。

必须完成完整闭环和生产级基础状态。不在截止前加入多 Agent、教师后台、排行榜或支付系统。
