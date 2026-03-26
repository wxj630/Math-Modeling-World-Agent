from __future__ import annotations

import os
import textwrap
from pathlib import Path

import jupyter_client

from mmw_agent.tools.base_interpreter import BaseCodeInterpreter, CodeExecutionResult
from mmw_agent.tools.notebook_serializer import NotebookSerializer


class LocalCodeInterpreter(BaseCodeInterpreter):
    def __init__(self, work_dir: str, notebook_serializer: NotebookSerializer):
        super().__init__(work_dir=work_dir, notebook_serializer=notebook_serializer)
        self.km = None
        self.kc = None
        self.interrupt_signal = False

    def initialize(self) -> None:
        self.km, self.kc = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self._pre_execute_code()

    def _pre_execute_code(self) -> None:
        escaped_work_dir = self.work_dir.replace("\\", "\\\\").replace("'", "\\'")
        init_code = textwrap.dedent(
            """
            import os
            from pathlib import Path

            work_dir = r'__MMW_WORK_DIR__'
            os.makedirs(work_dir, exist_ok=True)
            os.chdir(work_dir)
            print('Current working directory:', os.getcwd())

            def _mmw_enable_chinese_fonts():
                try:
                    import matplotlib.pyplot as plt
                    from matplotlib import font_manager as fm
                except Exception as e:
                    print(f"[mmw] matplotlib init skipped: {e}")
                    return None

                candidates = [
                    # macOS
                    "PingFang SC", "Hiragino Sans GB", "Songti SC", "Heiti SC", "STHeiti", "Arial Unicode MS",
                    # Windows
                    "Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong", "NSimSun", "DengXian",
                    # Linux
                    "Noto Sans CJK SC", "Noto Sans SC", "WenQuanYi Zen Hei", "WenQuanYi Micro Hei",
                    "Source Han Sans SC", "Source Han Sans CN", "AR PL UMing CN", "AR PL UKai CN",
                    "Noto Sans CJK JP", "Noto Sans CJK TC", "Noto Sans CJK KR",
                ]

                font_paths = []
                custom_font = os.getenv("MMW_CHINESE_FONT_PATH", "").strip()
                if custom_font:
                    font_paths.append(Path(custom_font).expanduser())

                font_paths.extend(
                    [
                        Path(work_dir) / "fonts" / "NotoSansCJKsc-Regular.otf",
                        Path(work_dir) / "fonts" / "NotoSansSC-Regular.otf",
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

                seen = set()
                sans_unique = []
                for name in sans:
                    if name in seen:
                        continue
                    sans_unique.append(name)
                    seen.add(name)

                plt.rcParams["font.family"] = "sans-serif"
                plt.rcParams["font.sans-serif"] = sans_unique
                plt.rcParams["axes.unicode_minus"] = False
                effective = selected or sans_unique[0]
                if selected is None:
                    print(
                        "[mmw] WARNING: No CJK font found; Chinese may render as squares. "
                        "Set MMW_CHINESE_FONT_PATH to a local .ttf/.otf."
                    )
                return effective

            def mmw_plot_style():
                # Keep this as a reusable helper for generated code cells.
                selected_font = _mmw_enable_chinese_fonts()
                try:
                    import matplotlib.pyplot as plt
                    import seaborn as sns

                    plt.rcParams.update(
                        {
                            "font.size": 11,
                            "axes.titlesize": 12,
                            "axes.titleweight": "bold",
                            "axes.labelsize": 11,
                            "axes.linewidth": 1.2,
                            "axes.spines.top": False,
                            "axes.spines.right": False,
                            "xtick.labelsize": 10,
                            "ytick.labelsize": 10,
                            "legend.fontsize": 10,
                            "legend.frameon": False,
                            "figure.dpi": 300,
                            "savefig.dpi": 300,
                            "savefig.bbox": "tight",
                            "savefig.pad_inches": 0.1,
                        }
                    )
                    sns.set_theme(style="ticks")
                    # seaborn set_theme can mutate rcParams; apply CJK fallback again.
                    _mmw_enable_chinese_fonts()
                except Exception:
                    pass
                return selected_font

            # Register a runtime module so generated code can safely do:
            #   from mmw_tools import mmw_plot_style
            try:
                import sys
                import types

                _mmw_tools_mod = types.ModuleType("mmw_tools")
                _mmw_tools_mod.mmw_plot_style = mmw_plot_style
                _mmw_tools_mod._mmw_enable_chinese_fonts = _mmw_enable_chinese_fonts
                sys.modules["mmw_tools"] = _mmw_tools_mod
            except Exception:
                pass

            _mmw_selected_font = mmw_plot_style()
            print("[mmw] Matplotlib CJK font:", _mmw_selected_font)
            """
        )
        init_code = init_code.replace("__MMW_WORK_DIR__", escaped_work_dir)
        self.execute_code_raw(init_code)

    def execute_code(self, code: str) -> CodeExecutionResult:
        self.notebook_serializer.add_code_cell_to_notebook(code)

        text_to_model: list[str] = []
        error_occurred = False
        error_message = ""

        execution = self.execute_code_raw(code)

        for mark, out_str in execution:
            if mark in ("stdout", "execute_result_text", "display_text"):
                text_to_model.append(self.truncate_text(f"[{mark}]\n{out_str}"))
                self.notebook_serializer.add_code_cell_output_to_notebook(out_str)
            elif mark in ("execute_result_png", "execute_result_jpeg", "display_png", "display_jpeg"):
                text_to_model.append(f"[{mark}] image generated")
                if "png" in mark:
                    self.notebook_serializer.add_image_to_notebook(out_str, "image/png")
                else:
                    self.notebook_serializer.add_image_to_notebook(out_str, "image/jpeg")
            elif mark == "error":
                error_occurred = True
                error_message = self.truncate_text(self.delete_color_control_char(out_str))
                text_to_model.append(error_message)
                self.notebook_serializer.add_code_cell_error_to_notebook(out_str)

        combined = "\n".join(text_to_model)
        return CodeExecutionResult(text_to_model=combined, error_occurred=error_occurred, error_message=error_message)

    def execute_code_raw(self, code: str) -> list[tuple[str, str]]:
        msg_id = self.kc.execute(code)
        _ = msg_id
        msg_list = []
        while True:
            try:
                iopub_msg = self.kc.get_iopub_msg(timeout=1)
                msg_list.append(iopub_msg)
                if (
                    iopub_msg["msg_type"] == "status"
                    and iopub_msg["content"].get("execution_state") == "idle"
                ):
                    break
            except Exception:
                if self.interrupt_signal:
                    self.km.interrupt_kernel()
                    self.interrupt_signal = False
                continue

        all_output: list[tuple[str, str]] = []
        for iopub_msg in msg_list:
            msg_type = iopub_msg.get("msg_type")
            content = iopub_msg.get("content", {})
            data = content.get("data", {})

            if msg_type == "stream" and content.get("name") == "stdout":
                all_output.append(("stdout", content.get("text", "")))
            elif msg_type == "execute_result":
                if "text/plain" in data:
                    all_output.append(("execute_result_text", data["text/plain"]))
                if "image/png" in data:
                    all_output.append(("execute_result_png", data["image/png"]))
                if "image/jpeg" in data:
                    all_output.append(("execute_result_jpeg", data["image/jpeg"]))
            elif msg_type == "display_data":
                if "text/plain" in data:
                    all_output.append(("display_text", data["text/plain"]))
                if "image/png" in data:
                    all_output.append(("display_png", data["image/png"]))
                if "image/jpeg" in data:
                    all_output.append(("display_jpeg", data["image/jpeg"]))
            elif msg_type == "error":
                traceback = content.get("traceback", [])
                output = "\n".join(traceback)
                all_output.append(("error", self.delete_color_control_char(output)))

        return all_output

    def get_created_images(self, section: str) -> list[str]:
        _ = section
        current_images: set[str] = set()
        for file in Path(self.work_dir).iterdir():
            if file.is_file() and file.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
                current_images.add(file.name)

        new_images = current_images - self.last_created_images
        self.last_created_images = current_images
        return sorted(new_images)

    def cleanup(self) -> None:
        if self.kc:
            self.kc.shutdown()
        if self.km:
            self.km.shutdown_kernel()

    def send_interrupt_signal(self) -> None:
        self.interrupt_signal = True

    def restart_jupyter_kernel(self) -> None:
        if self.kc:
            self.kc.shutdown()
        self.km, self.kc = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self.interrupt_signal = False
        os.makedirs(self.work_dir, exist_ok=True)
        self._pre_execute_code()
