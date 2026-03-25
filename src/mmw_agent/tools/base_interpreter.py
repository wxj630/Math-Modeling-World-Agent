from __future__ import annotations

import abc
import re
from dataclasses import dataclass

from mmw_agent.tools.notebook_serializer import NotebookSerializer


@dataclass
class CodeExecutionResult:
    text_to_model: str
    error_occurred: bool
    error_message: str


class BaseCodeInterpreter(abc.ABC):
    def __init__(self, work_dir: str, notebook_serializer: NotebookSerializer):
        self.work_dir = work_dir
        self.notebook_serializer = notebook_serializer
        self.section_output: dict[str, dict[str, list[str]]] = {}
        self.last_created_images: set[str] = set()

    @abc.abstractmethod
    def initialize(self) -> None:
        ...

    @abc.abstractmethod
    def execute_code(self, code: str) -> CodeExecutionResult:
        ...

    @abc.abstractmethod
    def cleanup(self) -> None:
        ...

    @abc.abstractmethod
    def get_created_images(self, section: str) -> list[str]:
        ...

    def add_section(self, section_name: str) -> None:
        if section_name not in self.section_output:
            self.section_output[section_name] = {"content": [], "images": []}

    def add_content(self, section: str, text: str) -> None:
        self.add_section(section)
        self.section_output[section]["content"].append(text)

    def get_code_output(self, section: str) -> str:
        self.add_section(section)
        return "\n".join(self.section_output[section]["content"])

    @staticmethod
    def delete_color_control_char(string: str) -> str:
        ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
        return ansi_escape.sub("", string)

    @staticmethod
    def truncate_text(text: str, max_length: int = 1000) -> str:
        if len(text) <= max_length:
            return text
        half_length = max_length // 2
        return text[:half_length] + "\n... (truncated) ...\n" + text[-half_length:]
