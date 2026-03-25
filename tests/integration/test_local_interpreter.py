from pathlib import Path

from mmw_agent.tools.local_interpreter import LocalCodeInterpreter
from mmw_agent.tools.notebook_serializer import NotebookSerializer


def test_local_interpreter_executes_and_writes_notebook(tmp_path: Path):
    serializer = NotebookSerializer(work_dir=tmp_path)
    interp = LocalCodeInterpreter(work_dir=str(tmp_path), notebook_serializer=serializer)
    interp.initialize()
    try:
        ok = interp.execute_code("x = 1\nprint(x)")
        assert "1" in ok.text_to_model
        assert not ok.error_occurred

        bad = interp.execute_code("raise ValueError('boom')")
        assert bad.error_occurred
        assert "ValueError" in bad.error_message
        assert serializer.notebook_path.exists()
    finally:
        interp.cleanup()

