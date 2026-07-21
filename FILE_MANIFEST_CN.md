# 文件清单与用途

## 根目录

- `README.md`：仓库用途、产品定义和关键入口。
- `START_HERE_CN.md`：第一次在 Codex 中操作的具体步骤。
- `AGENTS.md`：Codex 自动读取的长期产品、UX 与工程规则。
- `PROJECT_STATUS.md`：当前真实完成状态。
- `PLANS.md`：按依赖关系排列的开发里程碑。
- `STARTFRAME_FULL_SPEC_CN.md`：完整产品方案总入口。
- `CODEX_BUILD_LOG.md`：记录 Codex 贡献、人工决策、测试和 Session ID。
- `LICENSE`：MIT 开源许可证。
- `requirements.txt`：Python 运行与测试依赖。
- `.env.example`：不含密钥的本地配置模板。
- `Dockerfile`、`.dockerignore`、`render.yaml`、`DEPLOYMENT.md`：容器与 Render 评委 Demo 部署入口。

## `app/`

- `main.py`：FastAPI 路由、匿名 workspace、安全头与静态应用入口。
- `db.py`：SQLite schema、迁移和连接管理。
- `sources.py`、`learning.py`、`focus.py`：来源、地图与可恢复专注会话。
- `tutor.py`、`activities.py`、`mastery.py`：Guided Mastery Loop。
- `agent.py`、`search.py`：单动作规划 Agent 与四重门受控搜索。
- `ai.py`、`topic.py`：GPT-5.6 Responses API、结构化输出与主题备用来源。
- `records.py`：会话复制/删除、总结、导出、AI 活动和 workspace 数据控制。
- `static/`：全英文、纯色背景的生产 HTML/CSS/JavaScript UI。

## `tests/`

- 覆盖基础服务、来源、学习路径、专注会话、Tutor、练习、反馈、Evidence、Agent、搜索、主题备用路径与数据控制的自动化测试。

## `.github/`

- `workflows/tests.yml`：Python 3.13 自动测试与依赖完整性检查。

## `submission/`

- `JUDGE_TESTING_GUIDE.md`：无需 Key 的主评委路径与受控搜索路径。
- `DEVPOST_SUBMISSION.md`：完整英文 Devpost 文案和待替换链接。
- `DEMO_VIDEO_SCRIPT.md`：目标 2 分 50 秒的英文分镜与旁白。
- `FINAL_CHECKLIST.md`：官方提交规则、外部发布步骤和最终确认清单。

## `prototype/`

- `startframe_lowfi_prototype.html`：可点击的完整低保真原型。Codex 应检查布局、交互、状态和页面关系。
- `startframe_lowfi_overview.png`：由 HTML 原型导出的全页面总览，适合快速查看。
- `README_CN.md`：如何打开原型及其与生产代码的边界。

## `docs/`

1. `01_PRODUCT_SCOPE_AND_JUDGING_CN.md`：用户问题、受众、差异化、评分映射和 MVP 边界。
2. `02_INFORMATION_ARCHITECTURE_CN.md`：导航、页面层级、路由和信息结构。
3. `03_END_TO_END_USER_FLOW_CN.md`：从进入产品到恢复学习的完整主流程与分支。
4. `04_LOW_FIDELITY_PROTOTYPE_CN.md`：原型入口、页面编号、使用规则和 Codex 实现方法。
5. `05_SCREEN_AND_INTERACTION_SPEC_CN.md`：逐屏目标、内容、操作、状态和验收。
6. `06_COMPONENTS_AND_STATES_CN.md`：组件清单、状态矩阵、文案和复用规则。
7. `07_ADHD_INFORMED_UX_CN.md`：学习痛点到设计机制的映射及医学表述边界。
8. `08_GUIDED_MASTERY_LOOP_CN.md`：Tutor、Quiz、复述、提示、反馈、鼓励和补救练习。
9. `09_ADAPTIVE_AGENT_CN.md`：Agent 输入、动作、工具、决策边界和循环保护。
10. `10_SOURCE_GROUNDING_AND_SEARCH_CN.md`：来源解析、定位、标签、缺口和受控搜索。
11. `11_PRODUCTION_UX_STANDARDS_CN.md`：生产级加载、错误、保存、隐私、性能和可解释性规则。
12. `12_ACCESSIBILITY_RESPONSIVE_CN.md`：WCAG 2.2 AA 目标、键盘、焦点、语义和响应式布局。
13. `13_DATA_AI_API_CONTRACTS.md`：状态、数据实体、模型结构、API 语义和事件记录。
14. `14_ACCEPTANCE_AND_EVALS_CN.md`：单元、集成、浏览器、模型和人工验收。
15. `15_CODEX_STEP_BY_STEP_CN.md`：从规格仓库到提交的完整 Codex 操作方法。
16. `16_CODEX_PROMPTS_CN.md`：每个里程碑可直接复制给 Codex 的 Prompt。
17. `17_DEMO_AND_SUBMISSION_CN.md`：三分钟演示、评委测试路径和提交内容。
18. `18_DECISIONS_AND_SCOPE_CN.md`：最终决策与冲突解决优先级。

## `sample_data/`

- `transformer_notes.md`：主 Demo 学习材料。
- `matrix_prerequisite.md`：演示插入前置知识的材料。
- `demo_user_scenario.md`：固定演示用户、错误和预期 Agent 行为。

## `evals/`

- `CORE_PRODUCT_ACCEPTANCE_CASES.md`：核心业务闭环验收案例。
- `UI_UX_ACCEPTANCE_CASES.md`：页面、状态、无障碍和响应式验收案例。

## `references/`

- `DESIGN_STANDARDS_SOURCES.md`：W3C 与 OpenAI 官方实现依据。

## 检查文件

- `PACKAGE_VALIDATION_CN.md`：修订规格基线检查结果，包括 18 份编号规格、22 个原型视图、交互目标、JavaScript 语法、关键边界和竞赛提交约束。
- `PACKAGE_MANIFEST.json`：应用代码创建前的规格与原型基线文件大小、SHA-256 清单；后续应用文件不纳入此交付包清单。
