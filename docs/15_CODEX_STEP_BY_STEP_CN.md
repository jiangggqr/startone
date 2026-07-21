# 15 在 Codex 中从规格到完成项目

## 0. 准备

1. 解压整个 V4 文件夹。
2. 在 Codex App 打开根目录。
3. 打开 `prototype/startframe_lowfi_prototype.html`，先自己点击完整流程。
4. 新建一个主要开发 Thread。
5. 使用 `START_HERE_CN.md` 的第一条 Prompt，只阅读和规划。

## 1. 建立规格基线

让 Codex 初始化 Git，并提交：

```text
specification and UX prototype baseline
```

这一步不能创建应用代码。

## 2. 每个里程碑的固定流程

### A. 规划

让 Codex阅读相关规格和原型页面，列出：

- 目标
- 将创建或修改的文件
- 数据与状态
- UI 页面和组件
- 测试
- 风险

### B. 实现

粘贴 `16_CODEX_PROMPTS_CN.md` 中对应 Prompt。

### C. 验证

要求 Codex：

1. 运行相关单元和集成测试。
2. 启动应用。
3. 用内置浏览器操作变化后的完整流程。
4. 检查桌面和一个移动宽度。
5. 检查浏览器控制台。
6. 报告精确命令、结果和未完成项。

### D. 查看 diff

重点检查：

- 是否偏离原型和规格
- 是否遗漏错误状态
- 是否把 Agent 和 Tutor 混合
- 是否在前端暴露密钥
- 是否新增无必要依赖
- 是否把 Demo 数据冒充真实数据

### E. 提交

通过后：

```text
Update PLANS.md and CODEX_BUILD_LOG.md, then create a focused Git commit.
```

## 3. UI 实现检查方法

每个前端里程碑都让 Codex对照：

- `prototype/startframe_lowfi_prototype.html`
- `docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md`
- `docs/06_COMPONENTS_AND_STATES_CN.md`
- `docs/11_PRODUCTION_UX_STANDARDS_CN.md`
- `docs/12_ACCESSIBILITY_RESPONSIVE_CN.md`

不要只说“做得像原型”。要求它列出已实现的屏幕编号和状态。

## 4. 先 Demo 后真实 API

- Milestone 0–1：不调用模型，先完成确定性来源和基础状态。
- Milestone 2：接入第一个 GPT-5.6 Structured Outputs 路径，同时保留确定性 Demo fixtures。
- Milestone 3：使用已验证的 Demo/真实输出完成会话壳，不新增模型职责。
- Milestone 4：复用同一 AI gateway 接入 Tutor、练习与反馈。
- Milestone 5–6：接入 Agent 和命名材料缺口恢复。
- 所有模型输出先做 Schema 和来源校验。

## 5. API Key

只放在本地 `.env` 或部署 Secret。不能进入：

- Git
- Markdown
- 前端 JavaScript
- 截图和 Demo 视频

## 6. Codex 做错时

### 改动过大

```text
Stop. Do not add more features. Revert only the uncommitted changes from this task.
Propose a smaller implementation that satisfies the same acceptance criteria.
```

### 绕过测试

```text
Fix the root cause. Do not disable, weaken or delete the failing test.
Run the failing test first, then the full relevant suite.
```

### UI 与原型不一致

```text
Compare the implementation against prototype screen IDs and the screen specification.
List every mismatch before editing, then fix only those mismatches and verify them in the browser.
```

### Agent 越权

```text
The Agent may only select one next action. Move teaching, grading or encouragement behavior back into the Guided Mastery Loop.
Add a boundary test.
```

## 7. 记录竞赛开发过程

每阶段在 `CODEX_BUILD_LOG.md` 记录：

- Codex 加速了什么
- 你做了什么关键决策
- 哪些问题被纠正
- 运行了什么测试
- 对应 Session 和 commit

## 8. 提交前

- 全量测试
- 清理缓存、数据库、密钥和私有材料
- 验证无 Key Demo
- 验证真实 GPT-5.6
- 部署或可靠本地评委路径
- 录制三分钟以内视频
- 获取主要 Thread 的 `/feedback` Session ID
