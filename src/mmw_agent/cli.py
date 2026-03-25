from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mmw_agent.api import resume_math_modeling, run_math_modeling
from mmw_agent.config import settings
from mmw_agent.schemas import CompTemplate, FormatOutPut


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmw-agent", description="MathModeling workflow on ConnectOnion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a full math modeling workflow")
    run_parser.add_argument("--problem-file", required=True, help="Path to problem markdown/text file")
    run_parser.add_argument("--data-dir", required=True, help="Path to data directory")
    run_parser.add_argument("--output-dir", default=settings.DEFAULT_OUTPUT_DIR, help="Output root directory")
    run_parser.add_argument("--task-id", default=None, help="Optional task id")
    run_parser.add_argument("--comp-template", default=CompTemplate.CHINA.value, choices=[e.value for e in CompTemplate])
    run_parser.add_argument("--format-output", default=FormatOutPut.Markdown.value, choices=[e.value for e in FormatOutPut])
    run_parser.add_argument("--jupyter-host", default=settings.JUPYTER_HOST, help="Jupyter host")
    run_parser.add_argument("--jupyter-port", type=int, default=settings.JUPYTER_PORT, help="Jupyter port")
    run_parser.add_argument("--no-token", action="store_true", help="Disable Jupyter token authentication")
    run_parser.add_argument("--resume", action="store_true", help="Resume from existing server-side session state")
    run_parser.add_argument(
        "--shutdown-jupyter",
        action="store_true",
        help="Shutdown Jupyter when workflow exits (default keeps alive)",
    )

    resume_parser = subparsers.add_parser("resume", help="Resume a disconnected task from server-side session")
    resume_parser.add_argument("--task-id", required=True, help="Task id to resume")
    resume_parser.add_argument("--output-dir", default=settings.DEFAULT_OUTPUT_DIR, help="Output root directory")
    resume_parser.add_argument("--jupyter-host", default=None, help="Override Jupyter host")
    resume_parser.add_argument("--jupyter-port", type=int, default=None, help="Override Jupyter port")
    resume_parser.add_argument("--no-token", action="store_true", help="Disable Jupyter token authentication")
    resume_parser.add_argument(
        "--shutdown-jupyter",
        action="store_true",
        help="Shutdown Jupyter when workflow exits (default keeps alive)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        problem_file = Path(args.problem_file).expanduser().resolve()
        if not problem_file.exists():
            raise FileNotFoundError(f"Problem file not found: {problem_file}")
        problem_text = problem_file.read_text(encoding="utf-8")

        result = run_math_modeling(
            problem_text=problem_text,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            task_id=args.task_id,
            comp_template=CompTemplate(args.comp_template),
            format_output=FormatOutPut(args.format_output),
            jupyter_host=args.jupyter_host,
            jupyter_port=args.jupyter_port,
            jupyter_no_token=args.no_token or settings.JUPYTER_NO_TOKEN,
            jupyter_keep_alive=not args.shutdown_jupyter,
            resume=args.resume,
        )
    elif args.command == "resume":
        result = resume_math_modeling(
            task_id=args.task_id,
            output_dir=args.output_dir,
            jupyter_host=args.jupyter_host,
            jupyter_port=args.jupyter_port,
            jupyter_no_token=args.no_token or None,
            jupyter_keep_alive=not args.shutdown_jupyter,
        )
    else:
        parser.print_help()
        return 1

    print(f"Task ID: {result.task_id}")
    print(f"Resumed: {result.resumed}")
    print(f"Output Dir: {result.output_dir}")
    print(f"Notebook: {result.notebook_path}")
    print(f"Result Markdown: {result.result_md_path}")
    print(f"Result JSON: {result.result_json_path}")
    print(f"Session State: {result.session_state_path}")
    print(
        "Jupyter: "
        f"{result.jupyter_url} "
        f"(host={result.jupyter_host}, port={result.jupyter_port})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
