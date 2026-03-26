# 输出产物说明

每个任务会生成独立工作目录：`outputs/<task_id>/`。

## 关键文件

| 文件 | 说明 |
|---|---|
| `notebook.ipynb` | Coder 执行记录（代码 + 输出 + 图片） |
| `res.json` | 结构化结果 |
| `res.md` | 最终 markdown 成文 |
| `session_state.json` | session checkpoint，用于恢复 |

## `res.json` 差异

- `competition`：以章节/阶段结果为主
- `ai_tutor`：包含 `coordinator/modeler/coder/writer/images` 教学聚合结构

## 图片产物

- Coder 生成的图片会落在任务目录
- Writer 可引用图片名写入 `res.md`

## 建议归档方式

- 保留完整 `outputs/<task_id>/`
- 如需分享教学结果，至少包含：
  - `notebook.ipynb`
  - `res.md`
  - 图片文件
