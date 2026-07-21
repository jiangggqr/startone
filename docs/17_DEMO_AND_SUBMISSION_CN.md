# 17 Demo 与提交设计

## Official Rules 基线（再次核对于 2026-07-21）

- 提交截止：2026-07-21 17:00 Pacific Time，即 2026-07-22 08:00 新加坡时间
- 类别：Education
- 项目必须使用 Codex 与 GPT-5.6，能够稳定运行，并与视频和文字描述一致
- 本项目在 Submission Period 内从规格包开始实现；Git commit 与 Codex build log 用于证明新增工作
- 提供可免费测试的运行网站、可用 Demo 或测试构建，至少保持到评审期结束
- 所有提交材料必须为英文；中文视频或文字必须提供英文翻译
- 第三方代码、API、数据、音乐和商标必须有授权并遵守许可证
- 项目知识产权归参赛者；提交不得包含第三方机密、恶意代码、未授权版权内容或个人敏感信息
- 四项评分同权重：Technological Implementation、Design、Potential Impact、Quality of the Idea

## 三分钟内 Demo 建议

### 0:00–0:20 问题

展示一份复杂学习材料和空白学习意图：用户有材料，但不知道先做什么，也难以持续推进。

### 0:20–0:45 上传与来源

上传 Transformer 材料，展示真实页码、结构和来源标签。

### 0:45–1:05 学习地图与启动动作

展示 Agent 生成的知识地图和一个 90 秒动作。强调不是先给长课程。

### 1:05–1:35 Tutor

用户说“我不懂汇总是什么意思”。Tutor 连续问两个更小问题，再让用户自己连成一句。

### 1:35–2:00 Quiz / 复述 / 反馈

完成一题和一次简短复述，展示：已掌握、缺口、修正、具体鼓励。

### 2:00–2:25 补救与 Agent

展示错误驱动补救练习、LearningEvidence 和 Agent 推荐继续或插入前置知识。

### 2:25–2:40 受控搜索

展示只有明确缺口和用户确认后才搜索，并显示外部来源为何被选择。

### 2:40–2:55 总结与恢复

展示自动保存、下次两分钟动作和恢复卡片。

### 2:55–3:00 Codex 与 GPT-5.6

一句话说明 Codex 从规格和原型创建、测试并迭代项目；GPT-5.6 用于结构化知识地图、Tutor、练习、反馈、受控 Agent 决策，以及四重门通过后的 web search。

## 评委测试路径

README 首页提供：

1. 无 API Key 的 Demo mode
2. 固定样例材料
3. 一条完整流程
4. 真实模式配置
5. 预期 Agent 行为
6. 已知限制

受控搜索的稳定评委路径：

1. 新建会话并点击英文按钮 `Load controlled-search Demo`
2. 确认只有 `transformer_notes.md` 一份上传材料；完成设置时勾选允许系统建议外部搜索
3. 生成覆盖和路线；学习到 scaled dot-product attention 时向 Tutor 询问材料没有定义的 dot product
4. 完成一次未掌握的 Quiz 或自由复述并结束反馈，让事实性 `LearningEvidence.source_gap_signal` 与表现证据同时可用
5. 运行 Agent；它只能推荐一个 `request_search`，此时尚未发送任何搜索请求
6. 接受后检查独立确认页的命名缺口、范围、理由和四项门；点击确认才执行 Demo 搜索
7. 检查三个明确标记为 Demo 的 cited external sources；选择一个或无惩罚忽略，回到以上传材料为主的当前概念

## 必须提交

- 可运行项目
- Education 类别
- 项目描述
- 少于三分钟公开 YouTube 视频
- 代码仓库
- README、样例数据和运行说明
- Codex 与 GPT-5.6 使用说明
- 主要开发会话 `/feedback` Session ID
- 英文项目说明、英文 README/测试说明，以及英文演示音频或完整英文字幕
- 免费且无需评委重新构建的可测试 Demo URL（若使用本地路径，仍需同时提供可访问的测试构建）

## 需要突出

- Codex 如何把详细规格、原型和验收案例转成代码
- 你决定了 Agent/Tutor 边界、四重搜索门和 ADHD-informed UX
- GPT-5.6 如何通过 Structured Outputs 和受控工具调用实现可靠行为
- Demo 与真实模式怎样让评委稳定测试

## 提交前硬性复核

- Demo 视频必须少于 3 分钟；评委没有义务观看超出部分
- 视频必须公开托管于 YouTube，并用音频说明做了什么、怎样使用 Codex 和 GPT-5.6
- 仓库必须公开并带适用许可证，或私有共享给 `testing@devpost.com` 与 `build-week-event@openai.com`
- README 明确标出 Codex 加速点、人工产品/工程/设计决策和 GPT-5.6 的实际职责
- Devpost 草稿可在截止前修改；截止后不能实质修改提交内容
- 免费评委访问必须保持至评审期结束：2026-08-05 17:00 Pacific Time
