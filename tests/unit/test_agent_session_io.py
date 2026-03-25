from mmw_agent.core.agents.base import RoleAgentBase
from mmw_agent.schemas.enums import AgentRole


class FakeAgent:
    def __init__(self):
        self.current_session = None


class DummyRoleAgent(RoleAgentBase):
    def __init__(self, agent):
        super().__init__(
            role=AgentRole.COORDINATOR,
            system_prompt="x",
            agent=agent,
        )


def test_role_agent_session_export_import():
    fake = FakeAgent()
    role_agent = DummyRoleAgent(agent=fake)

    role_agent.import_session({"messages": [{"role": "system", "content": "s"}]})
    exported = role_agent.export_session()

    assert exported is not None
    assert exported["messages"][0]["content"] == "s"
