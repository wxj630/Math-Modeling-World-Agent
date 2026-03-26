# 故障排查

## 1. JSON 解析失败

现象：Coordinator / Modeler 报 JSON parse failed。

处理：

- 已内置 `json.loads -> json_repair -> 正则兜底` 修复链
- 检查模型是否输出大量非 JSON 文本
- 适当提升模型稳定性或降低 temperature

## 2. 中文绘图乱码

现象：matplotlib/seaborn 图中中文方块。

处理：

- 代码里调用 `mmw_plot_style()`
- 设置 `MMW_CHINESE_FONT_PATH`
- 避免强制 `font.family='Arial'`

## 3. Jupyter 端口占用

现象：`8888` 端口被其他服务占用。

处理：

- 使用 `--jupyter-port 8890` 等新端口
- 或复用已有 Jupyter（项目会尝试识别并复用）

## 4. 任务中断后重复跑

现象：网络抖动后只能重头开始。

处理：

- 使用 `mmw-agent resume --task-id ...`
- 确认 `session_state.json` 存在且路径正确

## 5. 依赖安装失败

现象：`uv pip install` 无法访问 PyPI。

处理：

- 检查网络/DNS
- 使用镜像源
- 在可联网环境先构建 wheel 后离线安装
