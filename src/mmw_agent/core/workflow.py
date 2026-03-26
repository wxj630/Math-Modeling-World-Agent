from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from mmw_agent.config import Settings, settings
from mmw_agent.core.agents import (
    CoderRoleAgent,
    CoordinatorRoleAgent,
    ModelerRoleAgent,
    WriterRoleAgent,
)
from mmw_agent.core.flows import Flows
from mmw_agent.core.session_store import WorkflowSessionStore
from mmw_agent.models import UserOutput
from mmw_agent.prompts import (
    CODER_TUTOR_PROMPT,
    COORDINATOR_TUTOR_PROMPT,
    MODELER_TUTOR_PROMPT,
    get_tutor_writer_prompt,
)
from mmw_agent.schemas import (
    CoordinatorToModeler,
    ModelerToCoder,
    Problem,
    WorkflowMode,
    WorkflowResult,
)
from mmw_agent.tools import (
    JupyterServerInfo,
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
        resume: bool = False,
    ) -> WorkflowResult:
        work_dir = create_work_dir(output_dir=output_dir, task_id=problem.task_id)
        store = WorkflowSessionStore(work_dir=work_dir)
        state = store.load() if resume else None
        resumed_from_state = resume and state is not None

        if state is None:
            state = store.new_state(
                task_id=problem.task_id,
                mode=problem.mode.value,
                problem_payload=problem.model_dump(mode="json"),
                data_dir=str(Path(data_dir).resolve()),
                output_dir=str(Path(output_dir).resolve()),
                jupyter={
                    "host": jupyter_host or self.cfg.JUPYTER_HOST,
                    "port": int(jupyter_port if jupyter_port is not None else self.cfg.JUPYTER_PORT),
                    "no_token": self.cfg.JUPYTER_NO_TOKEN if jupyter_no_token is None else jupyter_no_token,
                    "keep_alive": self.cfg.JUPYTER_KEEP_ALIVE if jupyter_keep_alive is None else jupyter_keep_alive,
                },
            )
        else:
            state.setdefault("mode", problem.mode.value)
            stages = state.setdefault("stages", {})
            stages.setdefault("tutor_coder_done", False)
            stages.setdefault("tutor_writer_done", False)
            artifacts = state.setdefault("artifacts", {})
            artifacts.setdefault("questions", None)
            artifacts.setdefault("ques_count", None)
            artifacts.setdefault("modeler_questions_solution", None)
            artifacts.setdefault("user_output_res", {})
            artifacts.setdefault(
                "tutor",
                {
                    "coordinator_response": None,
                    "modeler_response": None,
                    "coder_response": None,
                    "writer_response": None,
                    "created_images": [],
                },
            )
            state.setdefault(
                "agent_sessions",
                {"coordinator": None, "modeler": None, "coder": None, "writer": None},
            )

        mode = WorkflowMode(state.get("mode", problem.mode.value))
        if problem.mode != mode:
            problem.mode = mode

        if not resume or not any(work_dir.iterdir()):
            copy_data_to_work_dir(data_dir=data_dir, work_dir=work_dir)

        notebook_serializer = NotebookSerializer(work_dir=work_dir)
        code_interpreter = LocalCodeInterpreter(work_dir=str(work_dir), notebook_serializer=notebook_serializer)
        code_interpreter.initialize()

        host = jupyter_host or state["jupyter"]["host"]
        port = int(jupyter_port if jupyter_port is not None else state["jupyter"]["port"])
        no_token = state["jupyter"]["no_token"] if jupyter_no_token is None else jupyter_no_token
        keep_alive = state["jupyter"]["keep_alive"] if jupyter_keep_alive is None else jupyter_keep_alive

        jupyter_manager = JupyterServerManager(
            notebook_dir=work_dir,
            host=host,
            port=port,
            no_token=no_token,
            keep_alive=keep_alive,
        )
        jupyter_started = False
        if jupyter_manager.is_port_in_use(host=host, port=port):
            jupyter_info = JupyterServerInfo(
                host=host,
                port=port,
                url=f"http://{host}:{port}/tree",
                token_enabled=not no_token,
                notebook_dir=str(work_dir),
            )
        else:
            jupyter_info = jupyter_manager.start()
            jupyter_started = True

        try:
            coordinator_prompt_override = COORDINATOR_TUTOR_PROMPT if mode == WorkflowMode.AI_TUTOR else None
            modeler_prompt_override = MODELER_TUTOR_PROMPT if mode == WorkflowMode.AI_TUTOR else None
            coder_prompt_override = CODER_TUTOR_PROMPT if mode == WorkflowMode.AI_TUTOR else None
            writer_prompt_override = (
                get_tutor_writer_prompt(problem.format_output)
                if mode == WorkflowMode.AI_TUTOR
                else None
            )

            coordinator_agent = self.dependencies.coordinator_cls(
                cfg=self.cfg,
                system_prompt=coordinator_prompt_override,
            )

            modeler_agent = self.dependencies.modeler_cls(
                cfg=self.cfg,
                system_prompt=modeler_prompt_override,
            )

            coder_agent = self.dependencies.coder_cls(
                cfg=self.cfg,
                code_interpreter=code_interpreter,
                work_dir=str(work_dir),
                system_prompt=coder_prompt_override,
            )
            writer_agent = self.dependencies.writer_cls(
                cfg=self.cfg,
                comp_template=problem.comp_template,
                format_output=problem.format_output,
                scholar=OpenAlexScholar(email=self.cfg.OPENALEX_EMAIL),
                system_prompt=writer_prompt_override,
            )

            coordinator_agent.import_session(state["agent_sessions"].get("coordinator"))
            modeler_agent.import_session(state["agent_sessions"].get("modeler"))
            coder_agent.import_session(state["agent_sessions"].get("coder"))
            writer_agent.import_session(state["agent_sessions"].get("writer"))

            if mode == WorkflowMode.AI_TUTOR:
                result_json, result_md = self._execute_tutor_mode(
                    state=state,
                    store=store,
                    problem=problem,
                    work_dir=work_dir,
                    notebook_serializer=notebook_serializer,
                    coordinator_agent=coordinator_agent,
                    modeler_agent=modeler_agent,
                    coder_agent=coder_agent,
                    writer_agent=writer_agent,
                    code_interpreter=code_interpreter,
                )
            else:
                result_json, result_md = self._execute_competition_mode(
                    state=state,
                    store=store,
                    problem=problem,
                    work_dir=work_dir,
                    coordinator_agent=coordinator_agent,
                    modeler_agent=modeler_agent,
                    coder_agent=coder_agent,
                    writer_agent=writer_agent,
                    code_interpreter=code_interpreter,
                )

            state["stages"]["completed"] = True
            state["agent_sessions"]["coordinator"] = coordinator_agent.export_session()
            state["agent_sessions"]["modeler"] = modeler_agent.export_session()
            state["agent_sessions"]["coder"] = coder_agent.export_session()
            state["agent_sessions"]["writer"] = writer_agent.export_session()
            store.save(state)

            return WorkflowResult(
                task_id=problem.task_id,
                mode=mode,
                output_dir=str(work_dir),
                notebook_path=str(notebook_serializer.notebook_path),
                result_md_path=str(result_md),
                result_json_path=str(result_json),
                jupyter_host=jupyter_info.host,
                jupyter_port=jupyter_info.port,
                jupyter_url=jupyter_info.url,
                session_state_path=str(store.path),
                resumed=resumed_from_state,
            )
        except Exception:
            state["agent_sessions"]["coordinator"] = coordinator_agent.export_session() if "coordinator_agent" in locals() else None
            state["agent_sessions"]["modeler"] = modeler_agent.export_session() if "modeler_agent" in locals() else None
            state["agent_sessions"]["coder"] = coder_agent.export_session() if "coder_agent" in locals() else None
            state["agent_sessions"]["writer"] = writer_agent.export_session() if "writer_agent" in locals() else None
            store.save(state)
            raise
        finally:
            code_interpreter.cleanup()
            if jupyter_started:
                jupyter_manager.stop()

    def _execute_competition_mode(
        self,
        *,
        state: dict,
        store: WorkflowSessionStore,
        problem: Problem,
        work_dir: Path,
        coordinator_agent: CoordinatorRoleAgent,
        modeler_agent: ModelerRoleAgent,
        coder_agent: CoderRoleAgent,
        writer_agent: WriterRoleAgent,
        code_interpreter: LocalCodeInterpreter,
    ) -> tuple[Path, Path]:
        if state["stages"]["coordinator_done"] and state["artifacts"]["questions"] and state["artifacts"]["ques_count"]:
            coordinator_response = CoordinatorToModeler(
                questions=state["artifacts"]["questions"],
                ques_count=int(state["artifacts"]["ques_count"]),
            )
        else:
            coordinator_response = coordinator_agent.run(problem.ques_all)
            state["stages"]["coordinator_done"] = True
            state["artifacts"]["questions"] = coordinator_response.questions
            state["artifacts"]["ques_count"] = coordinator_response.ques_count
            state["agent_sessions"]["coordinator"] = coordinator_agent.export_session()
            store.save(state)

        if state["stages"]["modeler_done"] and state["artifacts"]["modeler_questions_solution"]:
            modeler_response = ModelerToCoder(
                questions_solution={k: str(v) for k, v in state["artifacts"]["modeler_questions_solution"].items()}
            )
        else:
            modeler_response = modeler_agent.run(coordinator_response)
            state["stages"]["modeler_done"] = True
            state["artifacts"]["modeler_questions_solution"] = modeler_response.questions_solution
            state["agent_sessions"]["modeler"] = modeler_agent.export_session()
            store.save(state)

        flows = Flows(coordinator_response.questions)
        config_template = get_config_template(problem.comp_template)
        user_output = UserOutput(work_dir=work_dir, ques_count=coordinator_response.ques_count)
        user_output.load_res(state["artifacts"].get("user_output_res", {}))

        solution_flows = flows.get_solution_flows(modeler_response)
        for key, value in solution_flows.items():
            if key in state["stages"]["solution_done_sections"]:
                continue
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
            state["stages"]["solution_done_sections"].append(key)
            state["artifacts"]["user_output_res"] = user_output.get_res()
            state["agent_sessions"]["coder"] = coder_agent.export_session()
            state["agent_sessions"]["writer"] = writer_agent.export_session()
            store.save(state)

        write_flows = flows.get_write_flows(
            user_output=user_output,
            config_template=config_template,
            bg_ques_all=problem.ques_all,
        )
        for key, value in write_flows.items():
            if key in state["stages"]["write_done_sections"]:
                continue
            writer_response = writer_agent.run(prompt=value, sub_title=key)
            user_output.set_res(key, writer_response)
            state["stages"]["write_done_sections"].append(key)
            state["artifacts"]["user_output_res"] = user_output.get_res()
            state["agent_sessions"]["writer"] = writer_agent.export_session()
            store.save(state)

        result_json, result_md = user_output.save_result()
        state["artifacts"]["user_output_res"] = user_output.get_res()
        return result_json, result_md

    def _execute_tutor_mode(
        self,
        *,
        state: dict,
        store: WorkflowSessionStore,
        problem: Problem,
        work_dir: Path,
        notebook_serializer: NotebookSerializer,
        coordinator_agent: CoordinatorRoleAgent,
        modeler_agent: ModelerRoleAgent,
        coder_agent: CoderRoleAgent,
        writer_agent: WriterRoleAgent,
        code_interpreter: LocalCodeInterpreter,
    ) -> tuple[Path, Path]:
        if state["stages"]["coordinator_done"] and state["artifacts"]["questions"] and state["artifacts"]["ques_count"]:
            coordinator_response = CoordinatorToModeler(
                questions=state["artifacts"]["questions"],
                ques_count=int(state["artifacts"]["ques_count"]),
            )
        else:
            coordinator_response = coordinator_agent.run(problem.ques_all)
            state["stages"]["coordinator_done"] = True
            state["artifacts"]["questions"] = coordinator_response.questions
            state["artifacts"]["ques_count"] = coordinator_response.ques_count
            state["artifacts"]["tutor"]["coordinator_response"] = coordinator_response.model_dump(mode="json")
            state["agent_sessions"]["coordinator"] = coordinator_agent.export_session()
            store.save(state)

        if state["stages"]["modeler_done"] and state["artifacts"]["modeler_questions_solution"]:
            modeler_response = ModelerToCoder(
                questions_solution={k: str(v) for k, v in state["artifacts"]["modeler_questions_solution"].items()}
            )
        else:
            modeler_response = modeler_agent.run(coordinator_response)
            state["stages"]["modeler_done"] = True
            state["artifacts"]["modeler_questions_solution"] = modeler_response.questions_solution
            state["artifacts"]["tutor"]["modeler_response"] = modeler_response.model_dump(mode="json")
            state["agent_sessions"]["modeler"] = modeler_agent.export_session()
            store.save(state)

        if not state["stages"]["tutor_coder_done"]:
            tutor_prompt = (
                "你要生成一个可教学实操的统计分布教程实验。\n"
                f"学习者原始请求:\n{problem.ques_all}\n\n"
                f"Coordinator 输出:\n{coordinator_response.questions}\n\n"
                f"Modeler 输出:\n{modeler_response.questions_solution}\n\n"
                "请在一个统一生活化例子下完成：概念对比、关系解释、代码实验、可视化、结果解释。"
            )
            coder_response = coder_agent.run(prompt=tutor_prompt, subtask_title="tutorial_lab")
            state["stages"]["tutor_coder_done"] = True
            state["artifacts"]["tutor"]["coder_response"] = {
                "code_response": coder_response.code_response,
                "code_output": coder_response.code_output,
            }
            state["artifacts"]["tutor"]["created_images"] = coder_response.created_images or []
            state["agent_sessions"]["coder"] = coder_agent.export_session()
            store.save(state)
        else:
            tutor_art = state["artifacts"]["tutor"]
            coder_response = type("CoderRes", (), tutor_art.get("coder_response", {}))()
            if getattr(coder_response, "code_response", None) is None:
                coder_response.code_response = ""
            if getattr(coder_response, "code_output", None) is None:
                coder_response.code_output = code_interpreter.get_code_output("tutorial_lab")

        if not state["stages"]["tutor_writer_done"]:
            writer_prompt = (
                "请根据以下内容撰写教学文档，输出高可读 markdown（含多级标题、代码片段、图片引用和解释）。\n\n"
                f"学习者需求:\n{problem.ques_all}\n\n"
                f"教学规划:\n{modeler_response.questions_solution}\n\n"
                f"代码执行总结:\n{getattr(coder_response, 'code_response', '')}\n"
                f"代码执行输出:\n{getattr(coder_response, 'code_output', '')}\n"
            )
            writer_response = writer_agent.run(
                prompt=writer_prompt,
                available_images=state["artifacts"]["tutor"]["created_images"],
                sub_title="tutorial",
            )
            state["stages"]["tutor_writer_done"] = True
            state["artifacts"]["tutor"]["writer_response"] = writer_response.model_dump(mode="json")
            state["agent_sessions"]["writer"] = writer_agent.export_session()
            store.save(state)
        else:
            writer_response = state["artifacts"]["tutor"]["writer_response"] or {"response_content": ""}
            writer_response = type("WriterRes", (), writer_response)()

        tutorial_md_text = str(getattr(writer_response, "response_content", ""))
        notebook_serializer.add_markdown_to_notebook(tutorial_md_text, title="Tutor Summary")

        res_json_path = work_dir / "res.json"
        res_md_path = work_dir / "res.md"
        res_json_path.write_text(
            json.dumps(
                {
                    "mode": WorkflowMode.AI_TUTOR.value,
                    "coordinator": state["artifacts"]["tutor"]["coordinator_response"],
                    "modeler": state["artifacts"]["tutor"]["modeler_response"],
                    "coder": state["artifacts"]["tutor"]["coder_response"],
                    "writer": state["artifacts"]["tutor"]["writer_response"],
                    "images": state["artifacts"]["tutor"]["created_images"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        res_md_path.write_text(tutorial_md_text, encoding="utf-8")
        return res_json_path, res_md_path
