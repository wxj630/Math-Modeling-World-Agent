from __future__ import annotations

import json

from mmw_agent.config import Settings, settings
from mmw_agent.prompts import MODELER_PROMPT
from mmw_agent.schemas.a2a import CoordinatorToModeler, ModelerToCoder
from mmw_agent.schemas.enums import AgentRole
from mmw_agent.utils import repair_json

from .base import RoleAgentBase


class ModelerRoleAgent(RoleAgentBase):
    def __init__(self, cfg: Settings = settings, agent=None):
        super().__init__(
            role=AgentRole.MODELER,
            system_prompt=MODELER_PROMPT,
            cfg=cfg,
            agent_name="mmw-modeler-agent",
            agent=agent,
        )

    def run(self, coordinator_to_modeler: CoordinatorToModeler) -> ModelerToCoder:
        prompt = json.dumps(coordinator_to_modeler.questions, ensure_ascii=False)
        max_retries = self.cfg.MAX_RETRIES
        response = self.agent.input(prompt, max_iterations=self.max_iterations)

        for attempt in range(max_retries + 1):
            repaired = repair_json(response)
            if repaired:
                return ModelerToCoder(questions_solution={k: str(v) for k, v in repaired.items()})
            if attempt >= max_retries:
                break
            response = self.agent.input(
                "你返回的JSON格式有误，请严格按照JSON格式重新输出，字符串内双引号要转义，不要输出额外文本。",
                max_iterations=self.max_iterations,
            )

        raise ValueError(f"Modeler JSON parse failed after {max_retries + 1} attempts")

