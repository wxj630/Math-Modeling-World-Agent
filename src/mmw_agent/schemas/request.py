from pydantic import BaseModel

from mmw_agent.schemas.enums import CompTemplate, FormatOutPut


class Problem(BaseModel):
    task_id: str
    ques_all: str
    comp_template: CompTemplate = CompTemplate.CHINA
    format_output: FormatOutPut = FormatOutPut.Markdown


class WorkflowResult(BaseModel):
    task_id: str
    output_dir: str
    notebook_path: str
    result_md_path: str
    result_json_path: str
    jupyter_host: str
    jupyter_port: int
    jupyter_url: str
