from __future__ import annotations

import os
from pathlib import Path


def _candidate_font_names() -> list[str]:
    return [
        # macOS
        "PingFang SC",
        "Hiragino Sans GB",
        "Songti SC",
        "Heiti SC",
        "STHeiti",
        "Arial Unicode MS",
        # Windows
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "FangSong",
        "NSimSun",
        "DengXian",
        # Linux
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei",
        "Source Han Sans SC",
        "Source Han Sans CN",
        "AR PL UMing CN",
        "AR PL UKai CN",
        "Noto Sans CJK JP",
        "Noto Sans CJK TC",
        "Noto Sans CJK KR",
    ]


def mmw_plot_style(work_dir: str | None = None) -> str | None:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm

    candidates = _candidate_font_names()

    font_paths: list[Path] = []
    custom_font = os.getenv("MMW_CHINESE_FONT_PATH", "").strip()
    if custom_font:
        font_paths.append(Path(custom_font).expanduser())

    if work_dir:
        wd = Path(work_dir)
        font_paths.extend(
            [
                wd / "fonts" / "NotoSansCJKsc-Regular.otf",
                wd / "fonts" / "NotoSansSC-Regular.otf",
            ]
        )

    font_paths.extend(
        [
            Path.home() / ".mmw_agent" / "fonts" / "NotoSansCJKsc-Regular.otf",
            Path.home() / ".mmw_agent" / "fonts" / "NotoSansSC-Regular.otf",
            Path.home() / ".cache" / "mmw_agent" / "fonts" / "NotoSansCJKsc-Regular.otf",
            Path.home() / ".cache" / "mmw_agent" / "fonts" / "NotoSansSC-Regular.otf",
        ]
    )

    for font_path in font_paths:
        if not font_path.exists():
            continue
        try:
            fm.fontManager.addfont(str(font_path))
            name = fm.FontProperties(fname=str(font_path)).get_name()
            if name and name not in candidates:
                candidates.insert(0, name)
        except Exception:
            continue

    available = {f.name for f in fm.fontManager.ttflist}
    selected = next((name for name in candidates if name in available), None)

    sans = []
    if selected:
        sans.append(selected)
    sans.extend([name for name in candidates if name in available and name not in sans])
    sans.append("DejaVu Sans")

    seen: set[str] = set()
    sans_unique: list[str] = []
    for name in sans:
        if name in seen:
            continue
        sans_unique.append(name)
        seen.add(name)

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = sans_unique
    plt.rcParams["axes.unicode_minus"] = False

    try:
        import seaborn as sns

        sns.set_theme(style="ticks")
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = sans_unique
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass

    if selected is None:
        print(
            "[mmw] WARNING: No CJK font found; Chinese may render as squares. "
            "Set MMW_CHINESE_FONT_PATH to a local .ttf/.otf."
        )
    return selected or sans_unique[0]


__all__ = ["mmw_plot_style"]
