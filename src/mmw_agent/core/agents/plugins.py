from __future__ import annotations

from typing import Any

from connectonion.useful_plugins import auto_compact, eval as eval_plugin, re_act

from mmw_agent.config import Settings
from mmw_agent.schemas.enums import AgentRole


PLUGIN_REGISTRY: dict[str, Any] = {
    "re_act": re_act,
    "auto_compact": auto_compact,
    "eval": eval_plugin,
}

DEFAULT_PLUGINS_BY_ROLE: dict[AgentRole, list[str]] = {
    AgentRole.COORDINATOR: ["re_act"],
    AgentRole.MODELER: ["re_act"],
    AgentRole.CODER: ["re_act", "auto_compact"],
    AgentRole.WRITER: ["re_act", "auto_compact"],
}


def resolve_plugin_names(
    role: AgentRole,
    settings: Settings,
    extra_plugin_names: list[str] | None = None,
) -> list[str]:
    resolved: list[str] = []
    for name in DEFAULT_PLUGINS_BY_ROLE.get(role, []):
        if name not in resolved:
            resolved.append(name)

    for name in settings.default_plugins:
        if name and name not in resolved:
            resolved.append(name)

    for name in settings.role_plugins.get(role.value, []):
        if name and name not in resolved:
            resolved.append(name)

    for name in extra_plugin_names or []:
        if name and name not in resolved:
            resolved.append(name)

    return resolved


def build_plugins(
    role: AgentRole,
    settings: Settings,
    extra_plugin_names: list[str] | None = None,
) -> list[Any]:
    plugin_names = resolve_plugin_names(role=role, settings=settings, extra_plugin_names=extra_plugin_names)
    plugins: list[Any] = []
    for name in plugin_names:
        plugin = PLUGIN_REGISTRY.get(name)
        if plugin is not None:
            plugins.append(plugin)
    return plugins

