from __future__ import annotations

from mmw_agent.config import Settings, settings
from mmw_agent.prompts import COORDINATOR_PROMPT
from mmw_agent.schemas.a2a import CoordinatorToModeler
from mmw_agent.schemas.enums import AgentRole
from mmw_agent.utils import parse_json_strict

from .base import RoleAgentBase


class CoordinatorRoleAgent(RoleAgentBase):
    def __init__(self, cfg: Settings = settings, agent=None, system_prompt: str | None = None):
        super().__init__(
            role=AgentRole.COORDINATOR,
            system_prompt=system_prompt or COORDINATOR_PROMPT,
            cfg=cfg,
            agent_name="mmw-coordinator-agent",
            agent=agent,
        )

    def run(self, ques_all: str) -> CoordinatorToModeler:
        max_retries = self.cfg.MAX_RETRIES
        response = self.agent.input(ques_all, max_iterations=self.max_iterations)
        for attempt in range(max_retries + 1):
            try:
                questions = parse_json_strict(response)
                ques_count = int(questions["ques_count"])
                return CoordinatorToModeler(questions=questions, ques_count=ques_count)
            except Exception as exc:
                if attempt >= max_retries:
                    raise RuntimeError(f"Coordinator JSON parse failed: {exc}") from exc
                response = self.agent.input(
                    f"⚠️ 上次响应格式错误: {exc}。请严格输出JSON格式，不要包含额外解释文本。",
                    max_iterations=self.max_iterations,
                )
        raise RuntimeError("Coordinator flow terminated unexpectedly")
