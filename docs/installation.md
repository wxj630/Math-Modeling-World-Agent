# 安装

## 环境要求

- Python `>=3.10`
- 推荐使用 `uv` 管理包安装
- 本项目默认依赖本地 `third_party/connectonion`

## 本地开发安装

```bash
source /Users/wuxiaojun/code/My-Agent/connectonion/.venv/bin/activate
cd /Users/wuxiaojun/code/My-Agent/Math-Modeling-World-Agent

uv pip install -e third_party/connectonion
uv pip install -e .
```

## 验证安装

```bash
mmw-agent --help
python -m pytest -q
```

## 可选：文档依赖

```bash
uv pip install -r docs/requirements.txt
```

## 可选：字体依赖（Linux 常见）

如果服务器没有中文字体，建议准备一个本地字体文件（如 Noto Sans CJK），并通过环境变量指定：

```bash
export MMW_CHINESE_FONT_PATH=/path/to/NotoSansCJKsc-Regular.otf
```
