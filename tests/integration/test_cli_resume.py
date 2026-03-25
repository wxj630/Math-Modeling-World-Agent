from pathlib import Path

from mmw_agent.cli import main
from mmw_agent.schemas.request import WorkflowResult


def test_cli_resume(monkeypatch, tmp_path: Path, capsys):
    def fake_resume_math_modeling(**kwargs):
        task_dir = tmp_path / "task-1"
        task_dir.mkdir(exist_ok=True)
        notebook = task_dir / "notebook.ipynb"
        res_md = task_dir / "res.md"
        res_json = task_dir / "res.json"
        notebook.write_text("{}", encoding="utf-8")
        res_md.write_text("# ok", encoding="utf-8")
        res_json.write_text("{}", encoding="utf-8")
        return WorkflowResult(
            task_id="task-1",
            output_dir=str(task_dir),
            notebook_path=str(notebook),
            result_md_path=str(res_md),
            result_json_path=str(res_json),
            jupyter_host="0.0.0.0",
            jupyter_port=8888,
            jupyter_url="http://0.0.0.0:8888/tree",
            session_state_path=str(task_dir / "session_state.json"),
            resumed=True,
        )

    monkeypatch.setattr("mmw_agent.cli.resume_math_modeling", fake_resume_math_modeling)

    code = main(["resume", "--task-id", "task-1", "--output-dir", str(tmp_path)])
    out = capsys.readouterr().out

    assert code == 0
    assert "Resumed: True" in out
