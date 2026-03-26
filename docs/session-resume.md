# Session 断线恢复

项目支持服务端落盘会话，不依赖 connectonion client 的 localStorage。

## 文件位置

每个任务目录下：

- `session_state.json`

例如：

```text
outputs/20260326-203600-8b2a9731/session_state.json
```

## 保存内容

- 任务元信息（`task_id`、`mode`、`problem`、`data_dir`）
- Jupyter 配置
- 阶段状态（`stages`）
- 中间产物（`artifacts`）
- 四角色会话（`agent_sessions`）

## 恢复方式

### 方式 1：`run --resume`

```bash
mmw-agent run \
  --task-id <task_id> \
  --problem-file <same_problem_file> \
  --data-dir <same_data_dir> \
  --output-dir <same_output_root> \
  --resume
```

### 方式 2：`resume`（推荐）

```bash
mmw-agent resume \
  --task-id <task_id> \
  --output-dir <same_output_root>
```

## 注意事项

- `task_id` 与 `output_dir` 必须指向原任务目录
- 如果你覆盖了 Jupyter host/port，恢复后会按新参数启动
- `session_state.json` 解析做了修复兜底，轻微 JSON 损坏可自动恢复
