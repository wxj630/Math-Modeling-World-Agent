from __future__ import annotations

from pathlib import Path

from mmw_agent.config import Settings, settings
from mmw_agent.core import MathModelWorkflow
from mmw_agent.core.session_store import WorkflowSessionStore
from mmw_agent.schemas import CompTemplate, FormatOutPut, Problem, WorkflowResult
from mmw_agent.utils import create_task_id


def run_math_modeling(
    *,
    problem_text: str,
    data_dir: str | Path,
    output_dir: str | Path | None = None,
    task_id: str | None = None,
    comp_template: CompTemplate = CompTemplate.CHINA,
    format_output: FormatOutPut = FormatOutPut.Markdown,
    jupyter_host: str | None = None,
    jupyter_port: int | None = None,
    jupyter_no_token: bool | None = None,
    jupyter_keep_alive: bool | None = None,
    resume: bool = False,
    cfg: Settings = settings,
) -> WorkflowResult:
    resolved_task_id = task_id or create_task_id()
    resolved_output_dir = output_dir or cfg.DEFAULT_OUTPUT_DIR

    problem = Problem(
        task_id=resolved_task_id,
        ques_all=problem_text,
        comp_template=comp_template,
        format_output=format_output,
    )

    workflow = MathModelWorkflow(cfg=cfg)
    return workflow.execute(
        problem=problem,
        data_dir=data_dir,
        output_dir=resolved_output_dir,
        jupyter_host=jupyter_host,
        jupyter_port=jupyter_port,
        jupyter_no_token=jupyter_no_token,
        jupyter_keep_alive=jupyter_keep_alive,
        resume=resume,
    )


def resume_math_modeling(
    *,
    task_id: str,
    output_dir: str | Path | None = None,
    jupyter_host: str | None = None,
    jupyter_port: int | None = None,
    jupyter_no_token: bool | None = None,
    jupyter_keep_alive: bool | None = None,
    cfg: Settings = settings,
) -> WorkflowResult:
    resolved_output_dir = Path(output_dir or cfg.DEFAULT_OUTPUT_DIR).expanduser().resolve()
    work_dir = resolved_output_dir / task_id
    store = WorkflowSessionStore(work_dir=work_dir)
    state = store.load()
    if not state:
        raise FileNotFoundError(f"Session state not found: {store.path}")

    problem_payload = state["problem"]
    data_dir = state["data_dir"]
    output_root = state["output_dir"]

    problem = Problem(
        task_id=problem_payload["task_id"],
        ques_all=problem_payload["ques_all"],
        comp_template=CompTemplate(problem_payload.get("comp_template", CompTemplate.CHINA.value)),
        format_output=FormatOutPut(problem_payload.get("format_output", FormatOutPut.Markdown.value)),
    )

    workflow = MathModelWorkflow(cfg=cfg)
    return workflow.execute(
        problem=problem,
        data_dir=data_dir,
        output_dir=output_root,
        jupyter_host=jupyter_host,
        jupyter_port=jupyter_port,
        jupyter_no_token=jupyter_no_token,
        jupyter_keep_alive=jupyter_keep_alive,
        resume=True,
    )
