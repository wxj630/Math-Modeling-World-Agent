from pathlib import Path

from mmw_agent.core.session_store import WorkflowSessionStore


def test_session_store_save_and_load(tmp_path: Path):
    store = WorkflowSessionStore(work_dir=tmp_path)
    state = store.new_state(
        task_id="task-1",
        problem_payload={"task_id": "task-1", "ques_all": "Q"},
        data_dir=str(tmp_path / "data"),
        output_dir=str(tmp_path),
        jupyter={"host": "0.0.0.0", "port": 8888, "no_token": True, "keep_alive": True},
    )
    state["stages"]["coordinator_done"] = True
    store.save(state)

    loaded = store.load()
    assert loaded is not None
    assert loaded["task_id"] == "task-1"
    assert loaded["stages"]["coordinator_done"] is True
    assert store.path.exists()
