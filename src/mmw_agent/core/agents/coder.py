from __future__ import annotations

import re

from mmw_agent.config import Settings, settings
from mmw_agent.prompts import CODER_PROMPT, get_reflection_prompt
from mmw_agent.schemas.a2a import CoderToWriter
from mmw_agent.schemas.enums import AgentRole
from mmw_agent.tools import BaseCodeInterpreter
from mmw_agent.utils import get_current_files

from .base import RoleAgentBase


class CoderRoleAgent(RoleAgentBase):
    def __init__(
        self,
        *,
        code_interpreter: BaseCodeInterpreter,
        work_dir: str,
        cfg: Settings = settings,
        agent=None,
    ):
        self.code_interpreter = code_interpreter
        self.work_dir = work_dir
        self.current_section = ""
        self._first_run = True
        self.max_retries = cfg.MAX_RETRIES

        super().__init__(
            role=AgentRole.CODER,
            system_prompt=CODER_PROMPT,
            tools=[self.execute_code],
            cfg=cfg,
            agent_name="mmw-coder-agent",
            agent=agent,
        )

    def execute_code(self, code: str) -> str:
        """Execute Python code in a persistent Jupyter kernel and return text output."""
        result = self.code_interpreter.execute_code(code)
        self.code_interpreter.add_content(self.current_section, result.text_to_model)
        if result.error_occurred:
            return f"CODE_EXECUTION_ERROR\n{result.error_message}"
        return result.text_to_model or "Code executed successfully."

    @staticmethod
    def _looks_like_failure(text: str) -> bool:
        if not text:
            return False
        patterns = [
            r"CODE_EXECUTION_ERROR",
            r"Traceback",
            r"\bException\b",
            r"\bNameError\b",
            r"\bSyntaxError\b",
            r"Task incomplete",
            r"失败",
            r"错误",
        ]
        return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)

    def run(self, prompt: str, subtask_title: str) -> CoderToWriter:
        self.current_section = subtask_title
        self.code_interpreter.add_section(subtask_title)

        run_prompt = prompt
        if self._first_run:
            self._first_run = False
            dataset_files = get_current_files(self.work_dir, "data")
            run_prompt = f"当前文件夹下的数据集文件: {dataset_files}\n\n{prompt}"

        retries = 0
        current_prompt = run_prompt

        while retries <= self.max_retries:
            response = self.agent.input(current_prompt, max_iterations=self.max_iterations)
            if self._looks_like_failure(response):
                retries += 1
                if retries > self.max_retries:
                    return CoderToWriter(
                        code_response=f"任务失败，超过最大尝试次数{self.max_retries}，最后错误信息: {response}",
                        code_output=self.code_interpreter.get_code_output(subtask_title),
                        created_images=[],
                    )
                current_prompt = get_reflection_prompt(response, "")
                continue

            return CoderToWriter(
                code_response=response,
                code_output=self.code_interpreter.get_code_output(subtask_title),
                created_images=self.code_interpreter.get_created_images(subtask_title),
            )

        return CoderToWriter(
            code_response=f"任务失败，超过最大尝试次数{self.max_retries}",
            code_output=self.code_interpreter.get_code_output(subtask_title),
            created_images=[],
        )

