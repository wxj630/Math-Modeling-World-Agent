# 快速开始

## 1. 激活环境

```bash
source /Users/wuxiaojun/code/My-Agent/connectonion/.venv/bin/activate
cd /Users/wuxiaojun/code/My-Agent/Math-Modeling-World-Agent
```

## 2. 安装依赖

```bash
uv pip install -e third_party/connectonion
uv pip install -e .
```

## 3. 运行赛题模式

```bash
mmw-agent run \
  --mode competition \
  --problem-file example/MCM-2017-C/Problem.md \
  --data-dir example/MCM-2017-C \
  --output-dir outputs \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token
```

## 4. 运行教学模式

```bash
mmw-agent run \
  --mode ai_tutor \
  --problem-file example/ai_tutor/distributions.md \
  --data-dir example/ai_tutor \
  --output-dir outputs \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token
```

## 5. 断线恢复

```bash
mmw-agent resume \
  --task-id <task_id> \
  --output-dir outputs
```

## 6. 查看结果

每个任务目录默认在 `outputs/<task_id>/`，包含：

- `notebook.ipynb`
- `res.json`
- `res.md`
- `session_state.json`
