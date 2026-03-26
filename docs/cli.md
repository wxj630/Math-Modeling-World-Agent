# CLI

入口命令：`mmw-agent`

```bash
mmw-agent --help
```

## 子命令

- `run`：启动新任务或在已有任务上 `--resume`
- `resume`：按 `task_id` 从服务端 session 文件恢复

## run

```bash
mmw-agent run \
  --problem-file <path> \
  --data-dir <path> \
  --output-dir outputs \
  --mode competition \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token
```

### 常用参数

| 参数 | 说明 |
|---|---|
| `--problem-file` | 题目 markdown/text 文件 |
| `--data-dir` | 数据目录 |
| `--output-dir` | 输出根目录，默认 `outputs` |
| `--task-id` | 自定义任务 id |
| `--mode` | `competition` 或 `ai_tutor` |
| `--comp-template` | `CHINA` / `AMERICAN` |
| `--format-output` | `Markdown` / `LaTeX` |
| `--resume` | 从已有 `session_state.json` 继续 |
| `--jupyter-host` / `--jupyter-port` | Jupyter 地址与端口 |
| `--no-token` | 禁用 Jupyter token |
| `--shutdown-jupyter` | 完成后关闭 Jupyter（默认保留） |

## resume

```bash
mmw-agent resume \
  --task-id <task_id> \
  --output-dir outputs
```

### 常用参数

| 参数 | 说明 |
|---|---|
| `--task-id` | 必填，目标任务 id |
| `--output-dir` | 输出根目录 |
| `--jupyter-host` / `--jupyter-port` | 可选覆盖 session 中配置 |
| `--no-token` | 可选禁用 token |
| `--shutdown-jupyter` | 完成后关闭 Jupyter |

## 命令输出

每次运行结束会打印：

- `Task ID`
- `Mode`
- `Resumed`
- `Output Dir`
- `Notebook`
- `Result Markdown`
- `Result JSON`
- `Session State`
- `Jupyter` URL + host + port
