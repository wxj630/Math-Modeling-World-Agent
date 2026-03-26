# Math Modeling World Agent 文档

`Math-Modeling-World-Agent` 是一个基于 `connectonion` 的后端多 Agent 数学建模工作流项目。

核心能力：

- 四角色协作：`Coordinator`、`Modeler`、`Coder`、`Writer`
- 双模式：`competition`（赛题）和 `ai_tutor`（教学）
- 内置 Jupyter Notebook 执行与可视化
- 断线恢复：服务端落盘 `session_state.json`
- 产物标准化输出：`notebook.ipynb`、`res.json`、`res.md`

## 文档导航

- [快速开始](quickstart.md)
- [安装](installation.md)
- [配置](configuration.md)
- [CLI](cli.md)
- [Python API](api.md)
- [Workflow](workflow.md)
- [模式说明](modes.md)
- [Session 断线恢复](session-resume.md)
- [Jupyter 与代码执行器](jupyter-and-interpreter.md)
- [输出产物说明](outputs.md)
- [故障排查](troubleshooting.md)
- [在线文档部署](deployment-github-pages.md)

## 适用场景

- 数模竞赛题自动化解题与论文初稿
- 教学型统计/建模笔记本生成
- 需要可追踪执行过程与断点续跑的长任务
