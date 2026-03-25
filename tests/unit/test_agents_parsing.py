from mmw_agent.core.agents.coordinator import CoordinatorRoleAgent
from mmw_agent.core.agents.modeler import ModelerRoleAgent
from mmw_agent.schemas.a2a import CoordinatorToModeler


class FakeAgent:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def input(self, prompt, max_iterations=None):
        self.calls.append((prompt, max_iterations))
        if not self._responses:
            raise RuntimeError("No more fake responses")
        return self._responses.pop(0)


def test_coordinator_parses_json_with_retry():
    fake = FakeAgent([
        "not json",
        '{"title":"t","background":"b","ques_count":1,"ques1":"q1"}',
    ])
    agent = CoordinatorRoleAgent(agent=fake)

    res = agent.run("problem")

    assert res.ques_count == 1
    assert res.questions["ques1"] == "q1"
    assert len(fake.calls) == 2


def test_modeler_repairs_and_parses_json():
    fake = FakeAgent([
        "{bad json",
        '{"eda":"do eda","ques1":"model","sensitivity_analysis":"sens"}',
    ])
    agent = ModelerRoleAgent(agent=fake)

    res = agent.run(CoordinatorToModeler(questions={"ques_count": 1, "ques1": "q1", "background": "bg"}, ques_count=1))

    assert "eda" in res.questions_solution
    assert res.questions_solution["ques1"] == "model"
    assert len(fake.calls) == 2
