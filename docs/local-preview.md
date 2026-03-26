# 本地预览文档

## 安装文档依赖

```bash
source /Users/wuxiaojun/code/My-Agent/connectonion/.venv/bin/activate
cd /Users/wuxiaojun/code/My-Agent/Math-Modeling-World-Agent
uv pip install -r docs/requirements.txt
```

## 启动本地站点

```bash
mkdocs serve
```

默认地址：

- `http://127.0.0.1:8000`

## 构建静态站点

```bash
mkdocs build
```

输出目录：

- `site/`

## 常见命令

```bash
mkdocs --version
mkdocs build --strict
```
