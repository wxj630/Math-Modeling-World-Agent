# 模式说明

## `competition`

面向正式数学建模赛题。

特征：

- 问题拆分更严格
- solution 段落和论文段落分阶段生成
- 输出强调论文结构化完整性

适合：MCM/ICM、国赛题、科研建模任务初稿。

## `ai_tutor`

面向教学与入门学习。

特征：

- 同样四角色，但流程更轻量
- 强调统一生活化案例串讲
- 代码与可视化实验优先
- 输出偏教学 notebook + 教学 markdown

适合：课堂演示、自学实验、知识点串讲。

## 选择建议

- 你要“解题+论文”：选 `competition`
- 你要“讲解+动手实验”：选 `ai_tutor`

## 切换方式

CLI：

```bash
mmw-agent run --mode competition ...
mmw-agent run --mode ai_tutor ...
```

API：

```python
from mmw_agent.schemas import WorkflowMode
mode = WorkflowMode.COMPETITION
# or WorkflowMode.AI_TUTOR
```
