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


def test_local_interpreter_chinese_plot_style_available(tmp_path: Path):
    serializer = NotebookSerializer(work_dir=tmp_path)
    interp = LocalCodeInterpreter(work_dir=str(tmp_path), notebook_serializer=serializer)
    interp.initialize()
    try:
        result = interp.execute_code(
            "\n".join(
                [
                    "import matplotlib.pyplot as plt",
                    "print('HAS_MMW_STYLE', callable(globals().get('mmw_plot_style')))",
                    "if 'mmw_plot_style' in globals():",
                    "    print('FONT_USED', mmw_plot_style())",
                    "plt.figure()",
                    "plt.plot([1, 2, 3], [1, 4, 9])",
                    "plt.title('中文标题')",
                    "plt.xlabel('横轴')",
                    "plt.ylabel('纵轴')",
                    "plt.savefig('cn_plot.png')",
                    "print('SAVED', 'cn_plot.png')",
                ]
            )
        )
        assert "HAS_MMW_STYLE" in result.text_to_model
        assert "True" in result.text_to_model
        assert not result.error_occurred
        assert (tmp_path / "cn_plot.png").exists()
    finally:
        interp.cleanup()


def test_local_interpreter_can_import_mmw_tools_module(tmp_path: Path):
    serializer = NotebookSerializer(work_dir=tmp_path)
    interp = LocalCodeInterpreter(work_dir=str(tmp_path), notebook_serializer=serializer)
    interp.initialize()
    try:
        result = interp.execute_code(
            "\n".join(
                [
                    "from mmw_tools import mmw_plot_style",
                    "font_name = mmw_plot_style()",
                    "print('IMPORTED_OK', bool(font_name))",
                ]
            )
        )
        assert "IMPORTED_OK" in result.text_to_model
        assert "True" in result.text_to_model
        assert not result.error_occurred
    finally:
        interp.cleanup()
