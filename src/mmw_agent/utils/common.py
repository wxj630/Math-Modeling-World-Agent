from __future__ import annotations

import datetime
import hashlib
import os
import shutil
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from importlib.resources import files

from mmw_agent.schemas.enums import CompTemplate


def create_task_id() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    random_hash = hashlib.md5(str(datetime.datetime.now()).encode("utf-8")).hexdigest()[:8]
    return f"{timestamp}-{random_hash}"


def create_work_dir(output_dir: str | Path, task_id: str) -> Path:
    output_path = Path(output_dir).expanduser().resolve()
    work_dir = output_path / task_id
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


def copy_data_to_work_dir(data_dir: str | Path, work_dir: str | Path) -> None:
    src = Path(data_dir).expanduser().resolve()
    dst = Path(work_dir).expanduser().resolve()
    if not src.exists():
        raise FileNotFoundError(f"Data directory not found: {src}")
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def get_current_files(folder_path: str | Path, kind: str = "all") -> list[str]:
    folder = Path(folder_path)
    if not folder.exists():
        return []
    files = [path.name for path in folder.iterdir() if path.is_file()]
    if kind == "all":
        return files
    if kind == "md":
        return [name for name in files if name.endswith(".md")]
    if kind == "ipynb":
        return [name for name in files if name.endswith(".ipynb")]
    if kind == "data":
        return [name for name in files if name.endswith((".xlsx", ".csv", ".xls"))]
    if kind == "image":
        return [name for name in files if name.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))]
    return files


def load_toml(path: str | Path) -> dict:
    with Path(path).open("rb") as f:
        return tomllib.load(f)


def get_config_template(comp_template: CompTemplate = CompTemplate.CHINA) -> dict:
    if comp_template != CompTemplate.CHINA:
        raise ValueError(f"Unsupported comp template for now: {comp_template}")
    template_path = files("mmw_agent.config") / "md_template.toml"
    return load_toml(template_path)
