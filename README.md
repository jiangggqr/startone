# StartFrame Agent

StartFrame Agent 是一个以用户上传材料为主要学习来源的学习 Agent Web App。本仓库包含完整产品规格、UI/UX 原型、验收要求，以及正在按里程碑实现的 FastAPI Web 应用。

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

## 当前实现

Milestone 0–4A 已建立：

- Python 3.11+ / FastAPI / Uvicorn 服务
- SQLite 初始化与 Schema 版本记录
- `GET /api/health` 健康检查
- 响应式、键盘可用的静态应用外壳
- 明确的 Demo / 真实模型模式标识
- 自动化基础测试
- 匿名 workspace Cookie 隔离与私有 UUID 文件保存
- PDF、Markdown、TXT 和粘贴文本导入
- 真实 PDF 页码、Markdown/TXT 标题与行号、粘贴文本段落定位
- 稳定来源/片段 ID、校验和、本地检索、重试与删除
- 英文来源清单、可核查预览、部分成功与可恢复错误状态
- 英文会话设置、自动本地草稿与服务端乐观版本控制
- 材料覆盖、明确候选缺口、2–5 个概念知识地图和可调整路线
- 一个带时长与完成条件的 60–120 秒启动动作
- 服务端 GPT-5.6 Responses API 网关与 Pydantic Structured Outputs
- 每个模型来源引用在保存和显示前经过 workspace、session、source 与 chunk 验证
- 明确分离的确定性 Demo 模式与真实模型模式
- 服务端版本化的启动回答与专注笔记，以及明确的双版本冲突选择
- 单一当前概念的三栏专注工作区与可核查来源返回路径
- 自动保存、离线本地保留、暂停/恢复锁、计时与刷新恢复
- 桌面、平板与 390px 手机端可完成的会话导航
- 保存退出总结和具体的下次启动动作
- 仅围绕当前概念的可恢复 Tutor 对话、六个快捷支持动作与自由提问
- 七级最少充分引导、检查问题、困惑信号和前置缺口事实信号
- 上传材料与 AI 补充解释的持续来源标签，以及每条 Tutor 引用的服务端验证
- Tutor 不改变路线、不生成 Agent 决策，也不具备网络搜索工具

Quiz、自由复述、反馈、Agent 与受控外部搜索会在后续里程碑逐步加入。未完成的功能不会用假数据冒充成功状态。

## 本地运行

需要 Python 3.11 或更高版本。

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

打开 `http://127.0.0.1:8000`。API 状态页位于 `http://127.0.0.1:8000/api/docs`。

运行测试：

```bash
source .venv/bin/activate
python -m pytest
```

默认使用不调用外部模型的 `demo` 模式。`.env` 不应提交；真实模型密钥只允许由服务端环境变量读取。

真实 GPT-5.6 模式需要在本地 `.env` 中设置 `STARTFRAME_MODE=real` 和 `OPENAI_API_KEY`。不要把 Key 粘贴到聊天、前端代码、文档或 Git 提交中。没有 Key 时，真实模式会返回明确的可恢复错误，不会静默切换或伪装成 Demo。

## 项目目录

```text
app/                    FastAPI 服务和静态前端
tests/                  自动化测试
docs/                   产品、交互、数据与验收规格
prototype/              低保真行为和布局参考
sample_data/            确定性 Demo 学习材料
evals/                  核心产品与 UI/UX 验收用例
```

详细开发顺序见 `PLANS.md`，重要产品边界和已决策项见 `docs/18_DECISIONS_AND_SCOPE_CN.md`。
