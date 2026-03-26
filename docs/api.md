# Python API

## `run_math_modeling`

```python
from mmw_agent import run_math_modeling
from mmw_agent.schemas import WorkflowMode

result = run_math_modeling(
    problem_text="...",
    data_dir="example/MCM-2017-C",
    output_dir="outputs",
    mode=WorkflowMode.COMPETITION,
)
print(result.model_dump())
```

### 关键参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `problem_text` | `str` | 题目原文 |
| `data_dir` | `str | Path` | 数据目录 |
| `output_dir` | `str | Path | None` | 输出根目录，空则用配置默认 |
| `task_id` | `str | None` | 任务 ID，不传则自动生成 |
| `mode` | `WorkflowMode` | `competition` / `ai_tutor` |
| `comp_template` | `CompTemplate` | `CHINA` / `AMERICAN` |
| `format_output` | `FormatOutPut` | `Markdown` / `LaTeX` |
| `resume` | `bool` | 是否在已有任务目录上断点续跑 |

## `resume_math_modeling`

```python
from mmw_agent import resume_math_modeling

result = resume_math_modeling(
    task_id="20260326-203600-8b2a9731",
    output_dir="outputs",
)
print(result.model_dump())
```

### 说明

- `resume_math_modeling` 会读取 `outputs/<task_id>/session_state.json`
- 从 session 中恢复 `problem`、`data_dir`、角色会话状态和阶段进度
- 从未完成阶段继续执行

## `WorkflowResult`

返回字段：

- `task_id`
- `mode`
- `output_dir`
- `notebook_path`
- `result_md_path`
- `result_json_path`
- `jupyter_host`
- `jupyter_port`
- `jupyter_url`
- `session_state_path`
- `resumed`
