from pathlib import Path

from mmw_agent.cli import main
from mmw_agent.schemas import WorkflowMode
from mmw_agent.schemas.request import WorkflowResult


def test_cli_run_tutor_mode_passed_to_api(monkeypatch, tmp_path: Path, capsys):
    problem = tmp_path / "problem.md"
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "outputs"
    data_dir.mkdir()
    output_dir.mkdir()
    problem.write_text("我是本科生，请用生活化例子讲正态分布和t分布", encoding="utf-8")

    captured = {}

    def fake_run_math_modeling(**kwargs):
        captured.update(kwargs)
        task_dir = output_dir / "task-1"
        task_dir.mkdir(exist_ok=True)
        notebook = task_dir / "notebook.ipynb"
        res_md = task_dir / "res.md"
        res_json = task_dir / "res.json"
        notebook.write_text("{}", encoding="utf-8")
        res_md.write_text("# tutor", encoding="utf-8")
        res_json.write_text("{}", encoding="utf-8")
        return WorkflowResult(
            task_id="task-1",
            mode=WorkflowMode.AI_TUTOR,
            output_dir=str(task_dir),
            notebook_path=str(notebook),
            result_md_path=str(res_md),
            result_json_path=str(res_json),
            jupyter_host="0.0.0.0",
            jupyter_port=8888,
            jupyter_url="http://0.0.0.0:8888/tree",
            session_state_path=str(task_dir / "session_state.json"),
            resumed=False,
        )

    monkeypatch.setattr("mmw_agent.cli.run_math_modeling", fake_run_math_modeling)

    code = main(
        [
            "run",
            "--problem-file",
            str(problem),
            "--data-dir",
            str(data_dir),
            "--output-dir",
            str(output_dir),
            "--mode",
            "ai_tutor",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert captured["mode"] == WorkflowMode.AI_TUTOR
    assert "Mode: ai_tutor" in out

