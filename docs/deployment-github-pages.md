# GitHub Pages 自动发布

项目已提供工作流：

- `.github/workflows/docs.yml`

## 触发条件

- push 到 `main` 且改动了：
  - `docs/**`
  - `mkdocs.yml`
  - `.github/workflows/docs.yml`
- 手动触发 `workflow_dispatch`

## 工作流做的事

1. 安装 Python
2. 安装 `docs/requirements.txt`
3. 执行 `mkdocs build --strict`
4. 上传 `site/` 到 GitHub Pages Artifact
5. 部署到 Pages

## 仓库设置

在 GitHub 仓库设置中确认：

1. `Settings -> Pages`
2. `Build and deployment` 选择 `GitHub Actions`

## 站点地址

默认地址通常为：

```text
https://<org-or-user>.github.io/<repo>/
```

请将 `mkdocs.yml` 里的：

- `site_url`
- `repo_url`

替换成你的真实仓库地址。
