from pathlib import Path

from mmw_agent.cli import main
from mmw_agent.schemas.request import WorkflowResult


def test_cli_smoke(monkeypatch, tmp_path: Path, capsys):
    problem = tmp_path / "problem.md"
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "outputs"
    data_dir.mkdir()
    output_dir.mkdir()
    problem.write_text("mock problem", encoding="utf-8")

    def fake_run_math_modeling(**kwargs):
        task_dir = output_dir / "task-1"
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
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "Task ID: task-1" in out
    assert "Jupyter:" in out

