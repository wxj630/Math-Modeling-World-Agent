from __future__ import annotations

import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JupyterServerInfo:
    host: str
    port: int
    url: str
    token_enabled: bool
    notebook_dir: str


class JupyterServerManager:
    def __init__(
        self,
        notebook_dir: str | Path,
        host: str = "0.0.0.0",
        port: int = 8888,
        no_token: bool = True,
        keep_alive: bool = True,
    ):
        self.notebook_dir = str(Path(notebook_dir).resolve())
        self.host = host
        self.port = port
        self.no_token = no_token
        self.keep_alive = keep_alive
        self.process: subprocess.Popen | None = None

    def start(self) -> JupyterServerInfo:
        cmd = [
            "jupyter",
            "notebook",
            "--no-browser",
            f"--ip={self.host}",
            f"--port={self.port}",
            f"--notebook-dir={self.notebook_dir}",
            "--ServerApp.allow_remote_access=True",
        ]

        if self.no_token:
            cmd.extend(
                [
                    "--ServerApp.token=",
                    "--ServerApp.password=",
                    "--NotebookApp.token=",
                    "--NotebookApp.password=",
                ]
            )

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        time.sleep(1)
        if self.process.poll() is not None:
            raise RuntimeError("Jupyter notebook server failed to start")

        url = f"http://{self.host}:{self.port}/tree"
        return JupyterServerInfo(
            host=self.host,
            port=self.port,
            url=url,
            token_enabled=not self.no_token,
            notebook_dir=self.notebook_dir,
        )

    def stop(self) -> None:
        if not self.process:
            return
        if self.keep_alive:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

    @staticmethod
    def is_port_in_use(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) == 0
