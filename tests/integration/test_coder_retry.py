from mmw_agent.core.agents.coder import CoderRoleAgent


class FakeAgent:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def input(self, prompt, max_iterations=None):
        self.calls.append(prompt)
        return self._responses.pop(0)


class DummyInterpreter:
    def __init__(self):
        self.sections = {}

    def add_section(self, name):
        self.sections.setdefault(name, [])

    def execute_code(self, code):
        raise AssertionError("execute_code should not be called in this mocked test")

    def add_content(self, section, text):
        self.sections.setdefault(section, []).append(text)

    def get_created_images(self, section):
        return []

    def get_code_output(self, section):
        return "\n".join(self.sections.get(section, []))


def test_coder_retries_after_error_text():
    fake_agent = FakeAgent(
        [
            "Traceback (most recent call last): CODE_EXECUTION_ERROR",
            "All done, outputs generated.",
        ]
    )
    coder = CoderRoleAgent(code_interpreter=DummyInterpreter(), work_dir=".", agent=fake_agent)

    res = coder.run("do task", "eda")

    assert "All done" in (res.code_response or "")
    assert len(fake_agent.calls) == 2

