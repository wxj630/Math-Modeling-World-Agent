from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkflowSessionStore:
    def __init__(self, work_dir: str | Path, filename: str = "session_state.json"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.work_dir / filename

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def new_state(
        self,
        *,
        task_id: str,
        mode: str,
        problem_payload: dict[str, Any],
        data_dir: str,
        output_dir: str,
        jupyter: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "version": 1,
            "task_id": task_id,
            "mode": mode,
            "problem": problem_payload,
            "data_dir": data_dir,
            "output_dir": output_dir,
            "jupyter": jupyter,
            "stages": {
                "coordinator_done": False,
                "modeler_done": False,
                "solution_done_sections": [],
                "write_done_sections": [],
                "tutor_coder_done": False,
                "tutor_writer_done": False,
                "completed": False,
            },
            "artifacts": {
                "questions": None,
                "ques_count": None,
                "modeler_questions_solution": None,
                "user_output_res": {},
                "tutor": {
                    "coordinator_response": None,
                    "modeler_response": None,
                    "coder_response": None,
                    "writer_response": None,
                    "created_images": [],
                },
            },
            "agent_sessions": {
                "coordinator": None,
                "modeler": None,
                "coder": None,
                "writer": None,
            },
            "updated_at": self._now_iso(),
        }

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: dict[str, Any]) -> None:
        state["updated_at"] = self._now_iso()
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(self.path)
