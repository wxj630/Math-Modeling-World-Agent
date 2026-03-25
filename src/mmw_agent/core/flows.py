from __future__ import annotations

from mmw_agent.models.user_output import UserOutput
from mmw_agent.schemas.a2a import ModelerToCoder
from mmw_agent.tools.base_interpreter import BaseCodeInterpreter


class Flows:
    def __init__(self, questions: dict[str, str | int]):
        self.questions = questions

    def get_solution_flows(self, modeler_response: ModelerToCoder) -> dict[str, dict[str, str]]:
        questions_quesx = {
            key: value
            for key, value in self.questions.items()
            if key.startswith("ques") and key != "ques_count"
        }
        solutions = modeler_response.questions_solution
        ques_flow = {
            key: {
                "coder_prompt": (
                    f"参考建模手给出的解决方案{solutions.get(key, '')}\n"
                    f"完成如下问题{value}"
                )
            }
            for key, value in questions_quesx.items()
        }
        flows = {
            "eda": {
                "coder_prompt": (
                    f"参考建模手给出的解决方案{solutions.get('eda', '对数据进行探索性分析')}\n"
                    "对当前目录下数据进行EDA分析(数据清洗,可视化),清洗后的数据保存当前目录下,不需要复杂的模型"
                )
            },
            **ques_flow,
            "sensitivity_analysis": {
                "coder_prompt": (
                    f"参考建模手给出的解决方案{solutions.get('sensitivity_analysis', '对模型进行灵敏度分析')}\n"
                    "完成敏感性分析"
                )
            },
        }
        return flows

    def get_write_flows(self, user_output: UserOutput, config_template: dict, bg_ques_all: str) -> dict[str, str]:
        model_build_solve = user_output.get_model_build_solve()
        return {
            "firstPage": f"问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['firstPage']}，撰写标题，摘要，关键词",
            "RepeatQues": f"问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['RepeatQues']}，撰写问题重述",
            "analysisQues": f"问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['analysisQues']}，撰写问题分析",
            "modelAssumption": f"问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['modelAssumption']}，撰写模型假设",
            "symbol": f"不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['symbol']}，撰写符号说明部分",
            "judge": f"不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template['judge']}，撰写模型的评价部分",
        }

    def get_writer_prompt(
        self,
        key: str,
        coder_response: str,
        code_interpreter: BaseCodeInterpreter,
        config_template: dict,
    ) -> str:
        code_output = code_interpreter.get_code_output(key)
        questions_quesx_keys = self.get_questions_quesx_keys()
        background = str(self.questions["background"])

        quesx_writer_prompt = {
            qkey: (
                f"问题背景{background},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template[qkey]}"
            )
            for qkey in questions_quesx_keys
        }

        writer_prompt = {
            "eda": f"问题背景{background},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template['eda']}",
            **quesx_writer_prompt,
            "sensitivity_analysis": f"问题背景{background},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template['sensitivity_analysis']}",
        }

        if key not in writer_prompt:
            raise ValueError(f"未知的任务类型: {key}")
        return writer_prompt[key]

    def get_questions_quesx_keys(self) -> list[str]:
        return list(self.get_questions_quesx().keys())

    def get_questions_quesx(self) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in self.questions.items()
            if key.startswith("ques") and key != "ques_count"
        }
