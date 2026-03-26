# Workflow

## 总体流程

1. 创建任务工作目录（`outputs/<task_id>`）
2. 初始化/恢复 `session_state.json`
3. 启动本地代码执行器（Jupyter kernel）
4. 启动或复用 Jupyter Notebook Server
5. 创建四角色 Agent 并恢复会话
6. 按 `mode` 进入具体流程
7. 保存阶段产物与角色会话
8. 返回 `WorkflowResult`

## 角色职责

- `Coordinator`：将题目整理为结构化问题（JSON）
- `Modeler`：给出问题对应建模方案（JSON）
- `Coder`：执行 Python 代码并记录 notebook
- `Writer`：生成最终文本内容并引用文献/图片

## competition 模式

流水线：

1. Coordinator 拆分题目
2. Modeler 生成 `eda + quesX + sensitivity_analysis`
3. Coder 执行每个 solution 子任务
4. Writer 逐段写 solution
5. Writer 再写完整论文章节
6. 汇总生成 `res.json` + `res.md`

## ai_tutor 模式

流水线：

1. Coordinator 结构化学习需求
2. Modeler 生成教学规划
3. Coder 生成统一案例教学实验（`tutorial_lab`）
4. Writer 生成教学型 Markdown
5. 同步写入 `res.json` + `res.md`，并将教学摘要写回 notebook

## checkpoint 机制

每个关键阶段都会写回 `session_state.json`：

- `stages`：阶段完成状态
- `artifacts`：中间产物
- `agent_sessions`：四角色会话

该机制用于断点续跑，避免网络中断后从头消耗 token。
