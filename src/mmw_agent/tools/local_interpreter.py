from __future__ import annotations

import os
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
        init_code = (
            "import os\n"
            f"work_dir = r'{self.work_dir}'\n"
            "os.makedirs(work_dir, exist_ok=True)\n"
            "os.chdir(work_dir)\n"
            "print('Current working directory:', os.getcwd())\n"
        )
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
