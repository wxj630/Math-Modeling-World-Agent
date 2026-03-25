from __future__ import annotations

from pathlib import Path

import ansi2html
import nbformat
from nbformat import v4 as nbf


class NotebookSerializer:
    def __init__(self, work_dir: str | Path, notebook_name: str = "notebook.ipynb"):
        self.nb = nbf.new_notebook()
        self.segmentation_output_content: dict[str, str] = {}
        self.current_segmentation: str = ""

        work_path = Path(work_dir)
        work_path.mkdir(parents=True, exist_ok=True)

        base = Path(notebook_name)
        notebook_filename = base.name if base.suffix == ".ipynb" else f"{base.name}.ipynb"
        self.notebook_path = work_path / notebook_filename

    def ansi_to_html(self, ansi_text: str) -> str:
        converter = ansi2html.Ansi2HTMLConverter()
        return converter.convert(ansi_text)

    def write_to_notebook(self) -> None:
        self.notebook_path.write_text(nbformat.writes(self.nb), encoding="utf-8")

    def add_code_cell_to_notebook(self, code: str) -> None:
        code_cell = nbf.new_code_cell(source=code)
        self.nb["cells"].append(code_cell)
        self.write_to_notebook()

    def add_code_cell_output_to_notebook(self, output: str) -> None:
        html_content = self.ansi_to_html(output)
        if self.current_segmentation:
            self.segmentation_output_content.setdefault(self.current_segmentation, "")
            self.segmentation_output_content[self.current_segmentation] += html_content

        cell_output = nbf.new_output(output_type="display_data", data={"text/html": html_content})
        self.nb["cells"][-1]["outputs"].append(cell_output)
        self.write_to_notebook()

    def add_code_cell_error_to_notebook(self, error: str) -> None:
        nbf_error_output = nbf.new_output(
            output_type="error",
            ename="Error",
            evalue="Error message",
            traceback=[error],
        )
        self.nb["cells"][-1]["outputs"].append(nbf_error_output)
        self.write_to_notebook()

    def add_image_to_notebook(self, image: str, mime_type: str) -> None:
        image_output = nbf.new_output(output_type="display_data", data={mime_type: image})
        self.nb["cells"][-1]["outputs"].append(image_output)
        self.write_to_notebook()

    def add_markdown_to_notebook(self, content: str, title: str | None = None) -> None:
        if title:
            content = f"##### {title}:\n{content}"
        markdown_cell = nbf.new_markdown_cell(content)
        self.nb["cells"].append(markdown_cell)
        self.write_to_notebook()

    def add_markdown_segmentation_to_notebook(self, content: str, segmentation: str) -> None:
        self.current_segmentation = segmentation
        self.segmentation_output_content[segmentation] = ""
        self.add_markdown_to_notebook(content, segmentation)

    def get_notebook_output_content(self, segmentation: str) -> str:
        return self.segmentation_output_content.get(segmentation, "")
