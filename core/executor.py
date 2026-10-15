"""
Local Windows Command & Shell Executor
Executes commands and scripts with sandboxing, process-tree management,
minimal environment isolation, and secret redaction via the ExecutionBoundary.
"""
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

from core.security.execution_boundary import ExecutionBoundary, StructuredExecutionResult

# Global event listeners registry
execution_listeners: List[Callable[[Dict[str, Any]], None]] = []

def register_execution_listener(callback: Callable[[Dict[str, Any]], None]):
    """Registers a listener function to receive execution updates."""
    if callback not in execution_listeners:
        execution_listeners.append(callback)

def notify_listeners(event: Dict[str, Any]):
    """Dispatches execution event to all registered listeners."""
    for listener in execution_listeners:
        try:
            listener(event)
        except Exception as e:
            print(f"[Executor Warning] Listener error: {e}", file=sys.stderr)

class WindowsSystemExecutor:
    """
    Sandboxed Windows code and command executor backed by ExecutionBoundary.
    """
    def __init__(self, workspace_dir: str, timeout: int = 180):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.boundary = ExecutionBoundary(
            workspace_dir=self.workspace_dir,
            default_timeout=timeout
        )
        self.boundary.register_listener(notify_listeners)
        self.execution_history: List[Dict[str, Any]] = []

    def execute_command(
        self,
        command: str,
        shell_type: str = "powershell",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a command inside the sandboxed workspace directory.
        Returns execution details: exit_code, stdout, stderr, duration, id.
        """
        res: StructuredExecutionResult = self.boundary.execute_command(
            command=command,
            shell_type=shell_type,
            cwd=str(self.workspace_dir),
            timeout=self.timeout,
            task_id=task_id
        )

        result_dict = {
            "id": res.command_id,
            "task_id": res.task_id,
            "command": res.args[-1] if res.args else command,
            "exit_code": res.exit_code,
            "output": res.output,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration": res.duration,
            "cwd": res.cwd,
            "success": res.exit_code == 0,
            "timed_out": res.timed_out,
            "truncated": res.truncated
        }

        self.execution_history.append(result_dict)
        return result_dict

    def execute_structured(
        self,
        executable: str,
        args: List[str],
        cwd: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes binary with structured argument array (no shell string expansion).
        """
        res = self.boundary.execute_structured(
            executable=executable,
            args=args,
            cwd=cwd,
            timeout=self.timeout,
            task_id=task_id
        )
        result_dict = res.to_dict()
        result_dict["success"] = res.exit_code == 0
        self.execution_history.append(result_dict)
        return result_dict

    def cancel_task_processes(self, task_id: str) -> int:
        """Kills all process trees spawned by a task."""
        return self.boundary.cancel_task_processes(task_id)

    def get_ag2_code_executor_wrapper(self, task_id: Optional[str] = None):
        """
        Creates an AG2-compatible executor function for code blocks with sandboxing.
        """
        def ag2_executor(code_blocks):
            all_outputs = []
            for code_block in code_blocks:
                if hasattr(code_block, "code"):
                    lang = getattr(code_block, "language", "powershell")
                    code = code_block.code
                elif isinstance(code_block, tuple):
                    lang, code = code_block
                else:
                    lang, code = "powershell", str(code_block)

                run_id = uuid.uuid4().hex[:8]

                if lang in ["python", "py"]:
                    temp_file = self.workspace_dir / f"_run_{run_id}.py"
                    self.boundary.safe_write_file(str(temp_file), code)
                    try:
                        res = self.boundary.execute_structured(
                            executable=sys.executable,
                            args=[str(temp_file)],
                            cwd=str(self.workspace_dir),
                            task_id=task_id
                        )
                    finally:
                        if temp_file.exists():
                            try:
                                temp_file.unlink()
                            except Exception:
                                pass
                elif lang in ["bash", "sh", "powershell", "ps1", "shell"]:
                    res = self.boundary.execute_command(code, shell_type="powershell", task_id=task_id)
                elif lang in ["bat", "cmd"]:
                    res = self.boundary.execute_command(code, shell_type="cmd", task_id=task_id)
                elif lang in ["javascript", "js", "node"]:
                    temp_file = self.workspace_dir / f"_run_{run_id}.js"
                    self.boundary.safe_write_file(str(temp_file), code)
                    try:
                        res = self.boundary.execute_structured(
                            executable="node",
                            args=[str(temp_file)],
                            cwd=str(self.workspace_dir),
                            task_id=task_id
                        )
                    finally:
                        if temp_file.exists():
                            try:
                                temp_file.unlink()
                            except Exception:
                                pass
                else:
                    res = self.boundary.execute_command(code, shell_type="powershell", task_id=task_id)

                output = res.output or (f"[Success, exit code 0]" if res.exit_code == 0 else f"[Failed, exit code {res.exit_code}]")
                all_outputs.append(f"Command Output:\n{output}")

            return 0, "\n\n".join(all_outputs)

        return ag2_executor
