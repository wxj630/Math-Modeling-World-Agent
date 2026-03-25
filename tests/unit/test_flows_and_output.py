from pathlib import Path

from mmw_agent.core.flows import Flows
from mmw_agent.models.user_output import UserOutput
from mmw_agent.schemas.a2a import ModelerToCoder, WriterResponse


class DummyInterpreter:
    def get_code_output(self, section):
        return f"output-{section}"


def test_flows_generates_solution_and_writer_prompts():
    questions = {
        "title": "t",
        "background": "bg",
        "ques_count": 2,
        "ques1": "q1",
        "ques2": "q2",
    }
    modeler = ModelerToCoder(
        questions_solution={
            "eda": "eda plan",
            "ques1": "m1",
            "ques2": "m2",
            "sensitivity_analysis": "splan",
        }
    )

    flows = Flows(questions)
    solution_flows = flows.get_solution_flows(modeler)
    assert set(solution_flows.keys()) == {"eda", "ques1", "ques2", "sensitivity_analysis"}

    template = {
        "eda": "tmpl-eda",
        "ques1": "tmpl-1",
        "ques2": "tmpl-2",
        "sensitivity_analysis": "tmpl-sens",
        "firstPage": "f",
        "RepeatQues": "r",
        "analysisQues": "a",
        "modelAssumption": "m",
        "symbol": "s",
        "judge": "j",
    }
    writer_prompt = flows.get_writer_prompt("ques1", "coder done", DummyInterpreter(), template)
    assert "tmpl-1" in writer_prompt


def test_user_output_dedupes_footnotes_and_saves(tmp_path: Path):
    out = UserOutput(work_dir=tmp_path, ques_count=1)
    out.set_res("firstPage", WriterResponse(response_content="A {[^1]: Ref A}", footnotes=[]))
    out.set_res("RepeatQues", WriterResponse(response_content="B", footnotes=[]))
    out.set_res("analysisQues", WriterResponse(response_content="C", footnotes=[]))
    out.set_res("modelAssumption", WriterResponse(response_content="D", footnotes=[]))
    out.set_res("symbol", WriterResponse(response_content="E", footnotes=[]))
    out.set_res("eda", WriterResponse(response_content="F", footnotes=[]))
    out.set_res("ques1", WriterResponse(response_content="G {[^2]: Ref A}", footnotes=[]))
    out.set_res("sensitivity_analysis", WriterResponse(response_content="H", footnotes=[]))
    out.set_res("judge", WriterResponse(response_content="I", footnotes=[]))

    res_json, res_md = out.save_result()

    assert res_json.exists()
    assert res_md.exists()
    text = res_md.read_text(encoding="utf-8")
    assert text.count("Ref A") == 1

