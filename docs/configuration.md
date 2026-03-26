# 配置

项目使用 `pydantic-settings`，默认从根目录 `.env` 加载配置。

## 必填配置

| 变量 | 说明 |
|---|---|
| `OPENALEX_EMAIL` | Writer 检索 OpenAlex 文献时必需 |
| `OPENAI_API_KEY` | 通用模型 API Key（未配置角色专用 Key 时使用） |
| `MODEL` | 通用模型名（未配置角色专用 model 时使用） |

## 角色级模型覆盖（可选）

| 变量 | 说明 |
|---|---|
| `COORDINATOR_MODEL` / `COORDINATOR_API_KEY` / `COORDINATOR_BASE_URL` | Coordinator 模型配置 |
| `MODELER_MODEL` / `MODELER_API_KEY` / `MODELER_BASE_URL` | Modeler 模型配置 |
| `CODER_MODEL` / `CODER_API_KEY` / `CODER_BASE_URL` | Coder 模型配置 |
| `WRITER_MODEL` / `WRITER_API_KEY` / `WRITER_BASE_URL` | Writer 模型配置 |

## 运行与重试

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `MAX_RETRIES` | `3` | JSON 解析失败重试次数 |
| `DEFAULT_OUTPUT_DIR` | `outputs` | 输出根目录 |

## Jupyter 相关

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `JUPYTER_HOST` | `0.0.0.0` | Notebook Server 监听地址 |
| `JUPYTER_PORT` | `8888` | Notebook Server 端口 |
| `JUPYTER_NO_TOKEN` | `true` | 是否关闭 token |
| `JUPYTER_KEEP_ALIVE` | `true` | 工作流结束后是否保留 Jupyter 进程 |

## 插件相关

| 变量 | 说明 |
|---|---|
| `MMW_DEFAULT_PLUGINS` | 默认插件列表（逗号分隔） |
| `MMW_PLUGINS_COORDINATOR` | Coordinator 额外插件 |
| `MMW_PLUGINS_MODELER` | Modeler 额外插件 |
| `MMW_PLUGINS_CODER` | Coder 额外插件 |
| `MMW_PLUGINS_WRITER` | Writer 额外插件 |

默认插件策略：

- Coordinator / Modeler: `re_act`
- Coder / Writer: `re_act,auto_compact`

## 中文字体配置（可选）

| 变量 | 说明 |
|---|---|
| `MMW_CHINESE_FONT_PATH` | 指向本地 `.ttf/.otf` 字体文件路径，解决 Linux 精简环境中文乱码 |

## 推荐 `.env` 示例

```env
MODEL=gpt-5.3-codex
OPENAI_API_KEY=...
OPENAI_BASE_URL=...

OPENALEX_EMAIL=you@example.com

JUPYTER_HOST=0.0.0.0
JUPYTER_PORT=8888
JUPYTER_NO_TOKEN=true
JUPYTER_KEEP_ALIVE=true

MMW_DEFAULT_PLUGINS=
MMW_PLUGINS_COORDINATOR=
MMW_PLUGINS_MODELER=
MMW_PLUGINS_CODER=
MMW_PLUGINS_WRITER=
```
