# 低保真原型说明

## 打开方法

双击或在浏览器中打开：

`startframe_lowfi_prototype.html`

桌面宽度下左侧导航可以切换全部页面。原型中的主要按钮会跳转到对应状态；状态卡是行为与文案参考，不保存真实数据。

## 总览模式

在 URL 后添加：

```text
?board=1
```

例如：

```text
file:///.../startframe_lowfi_prototype.html?board=1
```

总览模式显示全部页面，用于快速检查功能覆盖。`startframe_lowfi_overview.png` 就是从该模式导出的。

## Codex 使用方法

Codex 不应把原型 HTML 直接复制成生产应用。它应：

1. 读取页面层级和交互关系。
2. 对照 `docs/05_SCREEN_AND_INTERACTION_SPEC_CN.md`。
3. 按 `docs/06_COMPONENTS_AND_STATES_CN.md` 抽取生产组件。
4. 实现服务端状态、API、可访问性和恢复逻辑。
5. 在浏览器中逐屏验证。

## 原型包含的功能

- 首页与会话历史
- 无前置表单的材料上传与 AI 学习重点生成
- 文件上传、解析、材料清单和部分失败
- 可选查看的来源覆盖和缺口
- 简洁知识框架与直接开始的第一个概念讲解
- 专注学习工作区
- Contextual Tutor
- Quiz
- 自由复述和提示
- 即时反馈与具体鼓励
- 错误驱动补救练习
- LearningEvidence
- Agent 下一步
- 受控网络搜索
- 讲解内的轻量来源引用
- 总结和恢复
- 学习记录、隐私和数据删除
- 加载、空、部分成功、取消、重试、错误、权限、离线、保存冲突和恢复状态示例
- 桌面、平板、手机与键盘规则
