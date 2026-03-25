# Math-Modeling-World-Agent

基于 `connectonion` 实现的数学建模多 Agent 工作流，后端设计参考 `third_party/MathModelAgent/backend`，并保持其核心 Prompt 和流程分工。

## 功能概览

- 4 个独立角色 Agent：
  - `Coordinator Agent`：识别题目信息并拆分问题（JSON 输出）
  - `Modeler Agent`：给出每题建模方案（JSON 输出）
  - `Coder Agent`：调用 `local_interpreter` 在 Jupyter Kernel 中执行代码
  - `Writer Agent`：调用 `openalex_scholar` 检索文献并生成 Markdown 论文内容
- 工作流输出：
  - `notebook.ipynb`（实时代码执行记录）
  - `res.json`（章节中间结果）
  - `res.md`（最终论文 Markdown）
- 自动启动 Jupyter Notebook（默认 `0.0.0.0:8888`，默认无 token，默认任务结束后保留进程）

## 项目结构

```text
src/mmw_agent/
  api.py                    # Python API: run_math_modeling
  cli.py                    # CLI: mmw-agent run
  config/
    settings.py             # 环境变量配置
    md_template.toml        # 论文模板（从原仓库复制）
  core/
    workflow.py             # 主流程编排
    flows.py                # 分阶段 prompt 拼装
    agents/                 # 四角色 agent + plugin 解析
  tools/
    local_interpreter.py    # jupyter-client 执行器
    notebook_serializer.py  # ipynb 持久化
    jupyter_server.py       # Jupyter server 启停管理
    openalex_scholar.py     # OpenAlex 检索
  models/user_output.py     # 输出拼接与参考文献去重
  prompts/                  # 角色 prompts（含 shared）
```

## 安装

建议使用你现有虚拟环境：

```bash
source /Users/wuxiaojun/code/My-Agent/connectonion/.venv/bin/activate
cd /Users/wuxiaojun/code/My-Agent/Math-Modeling-World-Agent

# 安装 connectonion 本地版本（如果尚未安装）
uv pip install -e third_party/connectonion

# 安装当前项目
uv pip install -e .
```

## 环境变量

默认从项目根目录 `.env` 读取。

至少需要：

- `OPENALEX_EMAIL`（Writer 检索文献必需）
- 模型配置（二选一）：
  - 通用：`MODEL` + `OPENAI_API_KEY`（可配 `OPENAI_BASE_URL`）
  - 分角色覆盖：
    - `COORDINATOR_MODEL / COORDINATOR_API_KEY / COORDINATOR_BASE_URL`
    - `MODELER_MODEL / MODELER_API_KEY / MODELER_BASE_URL`
    - `CODER_MODEL / CODER_API_KEY / CODER_BASE_URL`
    - `WRITER_MODEL / WRITER_API_KEY / WRITER_BASE_URL`

可选 Jupyter 配置：

- `JUPYTER_HOST`（默认 `0.0.0.0`）
- `JUPYTER_PORT`（默认 `8888`）
- `JUPYTER_NO_TOKEN`（默认 `true`）
- `JUPYTER_KEEP_ALIVE`（默认 `true`）

可选插件配置：

- `MMW_DEFAULT_PLUGINS`
- `MMW_PLUGINS_COORDINATOR`
- `MMW_PLUGINS_MODELER`
- `MMW_PLUGINS_CODER`
- `MMW_PLUGINS_WRITER`

默认插件策略：

- Coordinator / Modeler: `re_act`
- Coder / Writer: `re_act,auto_compact`

## CLI 使用

```bash
mmw-agent run \
  --problem-file example/MCM-2017-C/Problem.md \
  --data-dir example/MCM-2017-C \
  --output-dir outputs \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token
```

运行后会打印：

- `Task ID`
- 输出目录
- `notebook.ipynb` 路径
- `res.md` / `res.json` 路径
- Jupyter URL（例如 `http://0.0.0.0:8888/tree`）

> 默认会保留 Jupyter 进程，方便你实时查看 notebook 执行过程。

如需任务结束后自动关闭 Jupyter：

```bash
mmw-agent run ... --shutdown-jupyter
```

## Python API 使用

```python
from mmw_agent import run_math_modeling

result = run_math_modeling(
    problem_text=open("example/MCM-2017-C/Problem.md", "r", encoding="utf-8").read(),
    data_dir="example/MCM-2017-C",
    output_dir="outputs",
)

print(result.model_dump())
```

## 测试

```bash
python -m pytest -q
```

当前测试覆盖：

- Coordinator / Modeler JSON 解析与重试
- Flows 生成逻辑
- UserOutput 引用去重与落盘
- 插件解析
- Local interpreter 执行与 notebook 写入
- Coder 错误重试
- CLI smoke

## 说明

- 本项目聚焦“后端工作流同构”，不包含前端/Redis/WebSocket 复刻。
- Prompt 以 `src/mmw_agent/prompts` 为准，保持与参考仓库一致。

# Acknowledgements
- https://github.com/openonion/connectonion
- https://github.com/jihe520/MathModelAgent
