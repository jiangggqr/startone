# 第一次在 Codex 中使用本规格包

## 1. 打开整个文件夹

在 Codex App 中打开 `startframe-agent-codex-spec-v4` 根目录。不要只上传原型图片。

## 2. 先查看原型

在浏览器中打开：

`prototype/startframe_lowfi_prototype.html`

- 左侧可切换全部页面。
- 原型内按钮可以演示主流程。
- 在地址后添加 `?board=1` 可看到全部页面总览。

## 3. 新建主要开发 Thread

尽量在一个主要 Thread 中完成核心功能，方便最终获取比赛要求的 `/feedback` Session ID。

## 4. 第一条 Prompt：只理解，不写代码

```text
Read AGENTS.md, PROJECT_STATUS.md, PLANS.md, STARTFRAME_FULL_SPEC_CN.md,
every file in docs/ in numerical order, prototype/README_CN.md,
and inspect prototype/startframe_lowfi_prototype.html.
Also read sample_data/ and evals/.

This repository intentionally contains specifications and a design prototype only.
Do not create application code yet.

Respond in concise Chinese:
1. Explain the product and the complete user journey.
2. Explain the boundary between Guided Mastery Loop and Adaptive Planning Agent.
3. Explain how uploaded sources, external sources and AI supplemental explanations differ.
4. Summarize the desktop, tablet and mobile UI structure.
5. List all loading, empty, error and recovery states that production implementation must support.
6. Identify any contradiction or missing decision.
7. Propose Milestone 0 only and list the exact files it would create.
```

## 5. 检查 Codex 的理解

它必须明确：

- 当前没有生产应用代码。
- HTML 是低保真交互原型，不是最终架构。
- 上传材料是默认主来源。
- Tutor、Quiz、复述、提示、反馈、鼓励和补救练习属于同一掌握循环。
- `LearningEvidence` 只记录事实，不包含推荐。
- Agent 每次只选择一个下一动作。
- 网络搜索需要会话允许、验证后的明确缺口、Agent 请求和用户本次确认。
- UI 必须实现加载、空、错误、部分成功和恢复状态。

## 6. 保存规格基线

```text
Initialize git if needed.
Commit the current specification and prototype state with the message:
"specification and UX prototype baseline"
Do not create application code in this step.
```

## 7. 开始 Milestone 0

打开 `docs/16_CODEX_PROMPTS_CN.md`，只复制 Prompt 0。每个里程碑完成、验证和提交后再继续下一个。
