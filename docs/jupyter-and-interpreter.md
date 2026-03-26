# Jupyter 与代码执行器

## 架构

- 代码执行器：`LocalCodeInterpreter`（基于 `jupyter-client`）
- notebook 序列化：`NotebookSerializer`
- Notebook Server：`JupyterServerManager`

执行代码时，单元会写入 `notebook.ipynb`，stdout/error/image 会被捕获并持久化。

## Jupyter 启动行为

默认行为：

- host: `0.0.0.0`
- port: `8888`
- token: 关闭（`--no-token`）
- 任务结束后保留进程（`keep_alive=true`）

如果端口已被占用，工作流会复用现有 Jupyter URL。

## 中文绘图支持

项目内置 `mmw_plot_style`，用于跨平台中文字体配置。

推荐在代码里这样写：

```python
from mmw_tools import mmw_plot_style
font_name = mmw_plot_style()
print("当前字体:", font_name)
```

### 字体兜底

如果系统没有可用 CJK 字体，会打印警告。此时请设置：

```bash
export MMW_CHINESE_FONT_PATH=/path/to/your/font.ttf
```

支持把字体放在以下路径之一：

- `<work_dir>/fonts/NotoSansCJKsc-Regular.otf`
- `~/.mmw_agent/fonts/NotoSansCJKsc-Regular.otf`
- `~/.cache/mmw_agent/fonts/NotoSansCJKsc-Regular.otf`

## 常见建议

- 教学模式建议每个可视化单元都调用一次 `mmw_plot_style()`
- 不要手工强制 `font.family='Arial'`，容易覆盖中文字体链
