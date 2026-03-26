from mmw_agent.utils.json_utils import parse_json_strict, repair_json


def test_parse_json_strict_extracts_json_object_from_mixed_text():
    raw = (
        "下面是结构化结果：\n"
        "```json\n"
        '{"title":"t","background":"b","ques_count":1,"ques1":"q1"}\n'
        "```\n"
        "请继续下一步。"
    )
    obj = parse_json_strict(raw)
    assert obj["ques_count"] == 1
    assert obj["ques1"] == "q1"


def test_repair_json_handles_trailing_comma_object():
    raw = '{"eda":"do eda","ques1":"model","sensitivity_analysis":"sens",}'
    obj = repair_json(raw)
    assert obj is not None
    assert obj["eda"] == "do eda"
    assert obj["ques1"] == "model"
