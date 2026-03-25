from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mmw_agent.config import Settings, settings
from mmw_agent.core.agents import (
    CoderRoleAgent,
    CoordinatorRoleAgent,
    ModelerRoleAgent,
    WriterRoleAgent,
)
from mmw_agent.core.flows import Flows
from mmw_agent.models import UserOutput
from mmw_agent.schemas import Problem, WorkflowResult
from mmw_agent.tools import (
    JupyterServerManager,
    LocalCodeInterpreter,
    NotebookSerializer,
    OpenAlexScholar,
)
from mmw_agent.utils import copy_data_to_work_dir, create_work_dir, get_config_template


@dataclass
class WorkflowDependencies:
    coordinator_cls: type[CoordinatorRoleAgent] = CoordinatorRoleAgent
    modeler_cls: type[ModelerRoleAgent] = ModelerRoleAgent
    coder_cls: type[CoderRoleAgent] = CoderRoleAgent
    writer_cls: type[WriterRoleAgent] = WriterRoleAgent


class MathModelWorkflow:
    def __init__(self, cfg: Settings = settings, dependencies: WorkflowDependencies | None = None):
        self.cfg = cfg
        self.dependencies = dependencies or WorkflowDependencies()

    def execute(
        self,
        *,
        problem: Problem,
        data_dir: str | Path,
        output_dir: str | Path,
        jupyter_host: str | None = None,
        jupyter_port: int | None = None,
        jupyter_no_token: bool | None = None,
        jupyter_keep_alive: bool | None = None,
    ) -> WorkflowResult:
        work_dir = create_work_dir(output_dir=output_dir, task_id=problem.task_id)
        copy_data_to_work_dir(data_dir=data_dir, work_dir=work_dir)

        notebook_serializer = NotebookSerializer(work_dir=work_dir)
        code_interpreter = LocalCodeInterpreter(work_dir=str(work_dir), notebook_serializer=notebook_serializer)
        code_interpreter.initialize()

        host = jupyter_host or self.cfg.JUPYTER_HOST
        port = int(jupyter_port if jupyter_port is not None else self.cfg.JUPYTER_PORT)
        no_token = self.cfg.JUPYTER_NO_TOKEN if jupyter_no_token is None else jupyter_no_token
        keep_alive = self.cfg.JUPYTER_KEEP_ALIVE if jupyter_keep_alive is None else jupyter_keep_alive

        jupyter_manager = JupyterServerManager(
            notebook_dir=work_dir,
            host=host,
            port=port,
            no_token=no_token,
            keep_alive=keep_alive,
        )
        jupyter_info = jupyter_manager.start()

        try:
            coordinator_agent = self.dependencies.coordinator_cls(cfg=self.cfg)
            modeler_agent = self.dependencies.modeler_cls(cfg=self.cfg)
            coder_agent = self.dependencies.coder_cls(
                cfg=self.cfg,
                code_interpreter=code_interpreter,
                work_dir=str(work_dir),
            )
            writer_agent = self.dependencies.writer_cls(
                cfg=self.cfg,
                comp_template=problem.comp_template,
                format_output=problem.format_output,
                scholar=OpenAlexScholar(email=self.cfg.OPENALEX_EMAIL),
            )

            coordinator_response = coordinator_agent.run(problem.ques_all)
            modeler_response = modeler_agent.run(coordinator_response)

            flows = Flows(coordinator_response.questions)
            config_template = get_config_template(problem.comp_template)
            user_output = UserOutput(work_dir=work_dir, ques_count=coordinator_response.ques_count)

            solution_flows = flows.get_solution_flows(modeler_response)
            for key, value in solution_flows.items():
                coder_response = coder_agent.run(prompt=value["coder_prompt"], subtask_title=key)
                writer_prompt = flows.get_writer_prompt(
                    key=key,
                    coder_response=coder_response.code_response or "",
                    code_interpreter=code_interpreter,
                    config_template=config_template,
                )
                writer_response = writer_agent.run(
                    prompt=writer_prompt,
                    available_images=coder_response.created_images or [],
                    sub_title=key,
                )
                user_output.set_res(key, writer_response)

            write_flows = flows.get_write_flows(
                user_output=user_output,
                config_template=config_template,
                bg_ques_all=problem.ques_all,
            )
            for key, value in write_flows.items():
                writer_response = writer_agent.run(prompt=value, sub_title=key)
                user_output.set_res(key, writer_response)

            result_json, result_md = user_output.save_result()

            return WorkflowResult(
                task_id=problem.task_id,
                output_dir=str(work_dir),
                notebook_path=str(notebook_serializer.notebook_path),
                result_md_path=str(result_md),
                result_json_path=str(result_json),
                jupyter_host=jupyter_info.host,
                jupyter_port=jupyter_info.port,
                jupyter_url=jupyter_info.url,
            )
        finally:
            code_interpreter.cleanup()
            jupyter_manager.stop()

