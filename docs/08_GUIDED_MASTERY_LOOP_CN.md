# 08 Guided Mastery Loop

## 职责

Guided Mastery Loop 负责当前概念怎样被解释、练习、反馈和补救。它不改变全局学习路线。

## 1. Contextual Tutor

### 输入

- 当前概念
- 相关来源片段
- 概念在知识地图中的关系
- AI 从材料生成的学习重点
- 最近已验证学习证据（用于校准支持）；开始学习前不收集基线回答
- 最近 Tutor 消息
- 最近尝试、提示和误解标签

### 支持动作

- 解释简单一点
- 定义术语
- 给具体例子
- 说明与上一概念的关系
- 只给提示
- 检查理解
- 自由问题

### 引导阶梯

1. 澄清具体困难
2. 给方向
3. 给结构
4. 给关键词
5. 给部分例子
6. 给简练解释
7. 提出检查问题

Tutor 可根据用户明确要求直接解释，但默认先使用最少足够支持。

## 2. Quiz

- 每个概念的 Quiz 固定为 3 道单选题，分别检查定义、机制和应用
- 单选题为 MVP 主形式；自由复述是独立的 1 题测试形式
- 每个错误选项对应 `misconception_tag`
- 提交前不泄露答案
- 提交后显示总分，并逐题解释该选项为什么正确或错误
- 题目和解释在后台带可验证来源引用；Quiz 界面不重复文件、页码和片段列表，只弱化标明来源类型
- 提示只在用户请求后原位出现，不显示锁定提示、提示计数说明或额外成功横幅

## 3. 自由复述

- 问题短且具体
- 允许自然语言改写
- 评估关键点覆盖，不依赖逐字匹配
- 提示逐级揭示
- 记录原始回答、修改、时间和提示深度

## 4. 即时反馈

后台统一结构：

```text
mastered_points
missing_or_unclear_points
misconceptions
compact_correction
next_micro_action
encouragement
source_refs
```

### 鼓励

必须引用用户的真实行为或已掌握内容。即使回答不正确，也可以肯定“完成了可检查的尝试”或“明确暴露了具体困难”。

`next_micro_action` 只能选择当前概念内的下一次练习、提示或补救，不能改变概念顺序、请求搜索或结束会话。需要全局转换时，先生成 Evidence，再交给 Agent。

学习者界面不逐项显示以上字段。Quiz 只合成为：总分、三条逐题正确 / 需要复习、所选答案、正确答案（答错时）、简短原因和一个 Continue；自由复述只保留结果、关键修正和 Continue。`next_micro_action`、误解标签和 Evidence 字段留在后台供掌握循环与 Agent 使用。

## 5. 补救练习

基于最新具体缺口生成：

- simpler_explanation
- smaller_question
- concrete_example
- contrast_question
- rephrase_task

连续两次相同策略无改善时停止重复，向 Agent 输出证据。

## 6. LearningEvidence

必须包含：

- activity_type: `tutor_check | quiz | recall | remedial`
- concept_id
- outcome
- key_point_coverage
- misconception_tags
- hint_depth
- elapsed_seconds
- tutor_confusion_signals
- remedial_result
- source_gap_signal
- timestamp

Tutor 不为每条消息单独生成 Evidence。在完成检查问题、用户明确表示仍困惑，或关闭本次 Tutor 会话时，将可观察信号聚合为一条记录。

`LearningEvidence` 不设默认学习者审阅页。用户从反馈继续时，系统在后台完成 Evidence 边界并自动请求 Agent 的一个下一动作。

`source_gap_signal` 只能描述材料未覆盖的已命名内容，是观察而不是搜索建议。

不得包含：

- next_action
- recommendation
- should_continue
- search_needed
- 隐藏推理过程

## 7. 边界

Guided Mastery Loop 不得：

- 改变概念顺序
- 自动搜索网络
- 插入前置知识
- 结束整个会话
- 把 AI 一般知识伪装成上传材料
