from __future__ import annotations

from typing import Any

from connectonion import Agent as ConnectOnionAgent
from connectonion.core.llm import LLM, LLMResponse, create_llm
from pydantic import BaseModel

from mmw_agent.config import Settings, settings
from mmw_agent.schemas.enums import AgentRole

from .plugins import build_plugins


class LLMWithDefaults(LLM):
    def __init__(self, inner: LLM, max_tokens: int | None = None):
        self.inner = inner
        self.max_tokens = max_tokens
        self.model = getattr(inner, "model", "")

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, **kwargs) -> LLMResponse:
        if self.max_tokens is not None:
            kwargs.setdefault("max_tokens", self.max_tokens)
        return self.inner.complete(messages, tools=tools, **kwargs)

    def structured_complete(self, messages: list[dict], output_schema: type[BaseModel], **kwargs) -> BaseModel:
        if self.max_tokens is not None:
            kwargs.setdefault("max_tokens", self.max_tokens)
        return self.inner.structured_complete(messages, output_schema, **kwargs)


def build_role_llm(cfg: Settings, role: AgentRole) -> LLM:
    raw_llm = create_llm(
        model=cfg.role_model(role),
        api_key=cfg.role_api_key(role),
        base_url=cfg.role_base_url(role),
    )
    return LLMWithDefaults(inner=raw_llm, max_tokens=cfg.role_max_tokens(role))


class RoleAgentBase:
    role: AgentRole
    system_prompt: str

    def __init__(
        self,
        *,
        role: AgentRole,
        system_prompt: str,
        tools: list[Any] | None = None,
        cfg: Settings = settings,
        extra_plugin_names: list[str] | None = None,
        agent_name: str | None = None,
        agent: ConnectOnionAgent | None = None,
    ):
        self.role = role
        self.system_prompt = system_prompt
        self.cfg = cfg
        self.max_iterations = cfg.role_max_iterations(role)

        if agent is not None:
            self.agent = agent
            return

        llm = build_role_llm(cfg, role)
        plugins = build_plugins(role=role, settings=cfg, extra_plugin_names=extra_plugin_names)
        self.agent = ConnectOnionAgent(
            name=agent_name or f"mmw-{role.value}-agent",
            llm=llm,
            tools=tools or [],
            system_prompt=system_prompt,
            max_iterations=self.max_iterations,
            plugins=plugins,
        )

