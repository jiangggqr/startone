# 06 组件、状态与文案规范

## 核心组件

### AppShell

包含全局导航、自动保存状态和帮助。学习会话中显示面包屑、暂停和退出；不得显示开发模式、模型名或评审控制。

### PrimaryActionCard

每屏最多一个。包含动作、原因、预计时间和主按钮。

### ConceptMap

支持当前、已完成、可进入、锁定和插入前置知识状态。不能只用颜色表达。

### SourceBadge

枚举：

- `uploaded`
- `external`
- `ai_supplement`

标签文字和视觉样式必须稳定一致。

`pasted` 是介质类型，在 SourceBadge 中映射为 `uploaded`，不增加第四个用户可见来源枚举。

### SourceViewer

显示文件、位置、片段、用途、来源类型和报告错误入口。

### TutorDrawer

包含上下文、消息、快捷问题、自由输入、发送状态、重试和关闭后焦点返回。

### ActivityCard

类型：Quiz、Recall、Remedial。包含来源、时间估计、提示和提交状态。

### HintLadder

`locked`、`available`、`revealed`。一次只揭示一级并记录深度。

### FeedbackPanel

固定五部分，不因题型改变核心结构。

### EvidenceSummary

只显示学习事实，不显示推荐。

Tutor 证据只在检查边界、明确困惑或关闭会话时聚合，不按消息逐条制造 Evidence。

### AgentDecisionCard

只显示一个推荐动作、理由、预计时间和“选择其他路径”。

替代动作必须来自服务端允许列表；不可用动作不显示为可操作 Radio。

### SaveIndicator

状态：正在保存、已保存、离线保存、保存失败、冲突。

## 跨组件状态

### 异步状态

- `idle`
- `loading`
- `streaming`
- `success`
- `partial_success`
- `error`
- `cancelled`
- `retrying`

### 表单状态

- pristine
- dirty
- validating
- invalid
- valid
- submitting
- submitted

### 按钮状态

- default
- hover
- focus-visible
- pressed
- disabled
- loading

加载按钮保留原宽度，并显示动作文字，例如“正在生成地图”，不只显示旋转图标。

## 文案规则

- 主按钮使用动词和结果：`生成学习地图`、`开始补救练习`。
- 避免模糊词：`确定`、`好的`、`继续`，除非上下文已非常明确。
- 错误文案包含发生了什么、是否保存、用户能做什么。
- 不使用“失败者”“注意力差”“你没有认真”等评价。
- 不用连续感叹号、强迫紧迫感或羞辱式连续打卡。

## 视觉优先级

1. 当前任务与主动作
2. 当前概念内容
3. 来源和支持工具
4. 进度与会话管理
5. 次要设置

同一屏不能有两个相同视觉强度的主按钮。

系统状态文档页可以并列展示多个状态卡，但每张状态卡内部仍只能有一个最强恢复动作；该文档页不作为生产任务页导航入口。
