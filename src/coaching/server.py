import atexit
import subprocess
import sys
import time
from typing import Optional

import requests


class OllamaServer:
    """
    Best-effort manager for a local Ollama server: starts `ollama serve` as a
    background subprocess if one isn't already listening on `host`, waits for
    it to come up, and (optionally) warms the target model into memory so the
    first real coaching call doesn't eat a slow cold-start load.
 
    If a server was already running before `start()` was called (e.g. the
    Windows tray-icon background service), this leaves it alone entirely --
    `stop()` only tears down a process *this* instance spawned.
    """
    
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: Optional[str] = None,
        startup_timeout: float = 30.0,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.startup_timeout = startup_timeout
        self._process: Optional[subprocess.Popen] = None
        self._started_by_us = False
        
    def is_running(self) -> bool:
        """Check if an Ollama server is already running at the specified host."""
        try:
            resp = requests.get(f"{self.host}", timeout=5.0)
            return resp.status_code == 200
        except requests.RequestException:
            return False
        
    def start(self, warm_up: bool = True):
        """Start the Ollama server if it's not already running, and optionally warm up the model."""
        if self.is_running():
            print(f"[ollama] server already running at {self.host}")
            return
        
        else:
            print("[ollama] no server found -- starting `ollama serve`...")
            self._spawn()
            self._wait_until_ready()
            self._started_by_us = True
            
        if warm_up and self.model:
            self._warm_up()
            
    
    def stop(self):
        """Shut down the server, but only if this instance is the one that started it."""
        if self._started_by_us and self._process:
            print("[ollama] stopping server...")
            self._process.terminate()
            try:
                self._process.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            self._started_by_us = False
            
    def _spawn(self):
        """Launch `ollama serve` as a detached background process."""
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        try:
            self._process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                "Failed to start Ollama server. Make sure `ollama` is installed and in your PATH."
            ) from e
            # Safety net: if main.py exits without reaching our finally block
            # (e.g. an unhandled exception elsewhere), still try to clean up
        atexit.register(self.stop)
            
    def _wait_until_ready(self):
        """Poll until the server responds or we give up."""
        deadline = time.time() + self.startup_timeout
        while time.time() < deadline:
            if self.is_running():
                print("[ollama] server is ready.")
                return
            if self._process and self._process.poll() is not None:
                if self.is_running():
                    print("[ollama] server is up (another instance grabbed the port first).")
                    self._started_by_us = False
                    return
                raise RuntimeError(
                    "The `ollama serve` process we started exited "
                    f"(exit code {self._process.returncode}) before becoming ready. "
                    "Check that Ollama isn't already running under a different host/port, "
                    "and that `ollama` is properly installed."
                )
            time.sleep(0.5)
        raise RuntimeError(f"Ollama server did not become ready within {self.startup_timeout} seconds.")
    
    def _warm_up(self):
        """Send a dummy request to the model to load it into memory."""
        print(f"[ollama] warming up model '{self.model}'...")
        try:
            requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello!"},
                    ],
                    "stream": False,
                    "options": {"temperature": 0.4, "num_predictions": 1},
                },
                timeout=self.startup_timeout,
            )
            print("[ollama] model warm-up complete.")
        except Exception as e:
            print(f"[ollama] warning: failed to warm up model: {e}")