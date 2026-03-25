from mmw_agent.config.settings import Settings
from mmw_agent.core.agents.plugins import build_plugins, resolve_plugin_names
from mmw_agent.schemas.enums import AgentRole


def test_plugin_resolution_defaults_and_env_overrides():
    cfg = Settings(
        MMW_DEFAULT_PLUGINS="eval",
        MMW_PLUGINS_CODER="re_act,eval",
    )

    names = resolve_plugin_names(AgentRole.CODER, cfg)
    assert names[0] == "re_act"
    assert "auto_compact" in names
    assert "eval" in names

    plugins = build_plugins(AgentRole.CODER, cfg)
    assert plugins
