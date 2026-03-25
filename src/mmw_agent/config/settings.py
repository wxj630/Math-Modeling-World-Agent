from __future__ import annotations

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from mmw_agent.schemas.enums import AgentRole


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    ENV: str = "dev"

    MODEL: str = "gpt-5.3-codex"
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None

    COORDINATOR_MODEL: str | None = None
    COORDINATOR_API_KEY: str | None = None
    COORDINATOR_BASE_URL: str | None = None
    COORDINATOR_MAX_TOKENS: int | None = None
    COORDINATOR_MAX_ITERATIONS: int = 8

    MODELER_MODEL: str | None = None
    MODELER_API_KEY: str | None = None
    MODELER_BASE_URL: str | None = None
    MODELER_MAX_TOKENS: int | None = None
    MODELER_MAX_ITERATIONS: int = 8

    CODER_MODEL: str | None = None
    CODER_API_KEY: str | None = None
    CODER_BASE_URL: str | None = None
    CODER_MAX_TOKENS: int | None = None
    CODER_MAX_ITERATIONS: int = 24

    WRITER_MODEL: str | None = None
    WRITER_API_KEY: str | None = None
    WRITER_BASE_URL: str | None = None
    WRITER_MAX_TOKENS: int | None = None
    WRITER_MAX_ITERATIONS: int = 12

    MAX_RETRIES: int = 3
    OPENALEX_EMAIL: str | None = None

    DEFAULT_OUTPUT_DIR: str = "outputs"

    JUPYTER_HOST: str = "0.0.0.0"
    JUPYTER_PORT: int = 8888
    JUPYTER_NO_TOKEN: bool = True
    JUPYTER_KEEP_ALIVE: bool = True

    MMW_DEFAULT_PLUGINS: str = ""
    MMW_PLUGINS_COORDINATOR: str = ""
    MMW_PLUGINS_MODELER: str = ""
    MMW_PLUGINS_CODER: str = ""
    MMW_PLUGINS_WRITER: str = ""

    default_plugins: list[str] = Field(default_factory=list)
    role_plugins: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _normalize_plugin_lists(self) -> "Settings":
        self.default_plugins = _split_csv(self.MMW_DEFAULT_PLUGINS)
        self.role_plugins = {
            AgentRole.COORDINATOR.value: _split_csv(self.MMW_PLUGINS_COORDINATOR),
            AgentRole.MODELER.value: _split_csv(self.MMW_PLUGINS_MODELER),
            AgentRole.CODER.value: _split_csv(self.MMW_PLUGINS_CODER),
            AgentRole.WRITER.value: _split_csv(self.MMW_PLUGINS_WRITER),
        }
        return self

    def role_model(self, role: AgentRole) -> str:
        mapping = {
            AgentRole.COORDINATOR: self.COORDINATOR_MODEL,
            AgentRole.MODELER: self.MODELER_MODEL,
            AgentRole.CODER: self.CODER_MODEL,
            AgentRole.WRITER: self.WRITER_MODEL,
        }
        return mapping[role] or self.MODEL

    def role_api_key(self, role: AgentRole) -> str | None:
        mapping = {
            AgentRole.COORDINATOR: self.COORDINATOR_API_KEY,
            AgentRole.MODELER: self.MODELER_API_KEY,
            AgentRole.CODER: self.CODER_API_KEY,
            AgentRole.WRITER: self.WRITER_API_KEY,
        }
        return mapping[role] or self.OPENAI_API_KEY

    def role_base_url(self, role: AgentRole) -> str | None:
        mapping = {
            AgentRole.COORDINATOR: self.COORDINATOR_BASE_URL,
            AgentRole.MODELER: self.MODELER_BASE_URL,
            AgentRole.CODER: self.CODER_BASE_URL,
            AgentRole.WRITER: self.WRITER_BASE_URL,
        }
        return mapping[role] or self.OPENAI_BASE_URL

    def role_max_tokens(self, role: AgentRole) -> int | None:
        mapping = {
            AgentRole.COORDINATOR: self.COORDINATOR_MAX_TOKENS,
            AgentRole.MODELER: self.MODELER_MAX_TOKENS,
            AgentRole.CODER: self.CODER_MAX_TOKENS,
            AgentRole.WRITER: self.WRITER_MAX_TOKENS,
        }
        return mapping[role]

    def role_max_iterations(self, role: AgentRole) -> int:
        mapping = {
            AgentRole.COORDINATOR: self.COORDINATOR_MAX_ITERATIONS,
            AgentRole.MODELER: self.MODELER_MAX_ITERATIONS,
            AgentRole.CODER: self.CODER_MAX_ITERATIONS,
            AgentRole.WRITER: self.WRITER_MAX_ITERATIONS,
        }
        return mapping[role]


settings = Settings()
