"""
Centralized Execution Boundary
Enforces strict security constraints for command execution and file operations:
- Approved workspace directory sandboxing (prevents traversal, symlinks, junction escapes)
- Minimal environment variable inheritance (prevents secret leaks to child processes)
- Process tree termination on Windows (kills full descendant process tree)
- Output size limits and execution timeouts
- Automated secret redaction
- Structured execution telemetry with command IDs and task IDs
"""
import os
import sys
import time
import re
import uuid
import signal
import subprocess
import threading
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable, Set

try:
    import psutil
except ImportError:
    psutil = None

# Whitelisted environment variables passed to child processes
SAFE_ENV_VARS = {
    "SYSTEMROOT",
    "SYSTEMDRIVE",
    "WINDIR",
    "PATH",
    "PATHEXT",
    "TEMP",
    "TMP",
    "COMSPEC",
    "USERPROFILE",
    "HOMEDRIVE",
    "HOMEPATH",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER",
    "OS",
    "LOCALAPPDATA",
    "APPDATA",
    "PROGRAMFILES",
    "PROGRAMFILES(X86)",
    "PROGRAMDATA"
}

# Regex patterns for secret redaction
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE),
    re.compile(r"(api[_\-]?key|auth[_\-]?token|secret|password|bearer\s+)[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{12,})['\"]?", re.IGNORECASE),
]

# Forbidden command substrings for safety
BLOCKED_COMMAND_PATTERNS = [
    re.compile(r"\bformat\s+[a-zA-Z]:", re.IGNORECASE),
    re.compile(r"\bdel\s+.*[\\/](windows|system32)\b", re.IGNORECASE),
    re.compile(r"\brmdir\s+.*[\\/](windows|system32)\b", re.IGNORECASE),
    re.compile(r"\b(stop-computer|restart-computer)\b", re.IGNORECASE),
    re.compile(r"\b(reg\s+delete|regedit)\b", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
]

@dataclass
class StructuredExecutionResult:
    command_id: str
    task_id: Optional[str]
    executable: str
    args: List[str]
    cwd: str
    exit_code: int
    duration: float
    timed_out: bool
    cancelled: bool
    stdout: str
    stderr: str
    output: str
    truncated: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExecutionBoundary:
    """
    Central gatekeeper for file I/O and process execution.
    """
    def __init__(
        self,
        workspace_dir: Path,
        allowed_dirs: Optional[List[Path]] = None,
        default_timeout: int = 120,
        max_output_chars: int = 50000,
        known_secrets: Optional[Set[str]] = None
    ):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_dirs = [self.workspace_dir]
        if allowed_dirs:
            for ad in allowed_dirs:
                self.allowed_dirs.append(Path(ad).resolve())

        self.default_timeout = default_timeout
        self.max_output_chars = max_output_chars
        self.known_secrets: Set[str] = set()
        if known_secrets:
            self.known_secrets.update(s for s in known_secrets if s and len(s) >= 6)

        # Collect secrets from current os.environ for automated redaction
        for k, v in os.environ.items():
            if any(term in k.upper() for term in ["KEY", "TOKEN", "SECRET", "PASSWORD"]):
                if v and len(v) >= 6:
                    self.known_secrets.add(v)

        # Active processes registry for cancellation
        self._active_processes: Dict[str, subprocess.Popen] = {}
        self._active_tasks: Dict[str, Set[str]] = {}  # task_id -> set of command_ids
        self._lock = threading.Lock()
        self.execution_listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]):
        if callback not in self.execution_listeners:
            self.execution_listeners.append(callback)

    def _notify_listeners(self, event: Dict[str, Any]):
        for listener in self.execution_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"[ExecutionBoundary Warning] Listener error: {e}", file=sys.stderr)

    # -------------------------------------------------------------------------
    # Path & File Security
    # -------------------------------------------------------------------------
    def resolve_safe_path(self, rel_or_abs_path: str, allow_create_parent: bool = False) -> Path:
        """
        Resolves path and guarantees it resides within an approved directory.
        Protects against traversal ('..'), symlinks, and junction escapes.
        """
        raw_path = Path(rel_or_abs_path)
        if raw_path.is_absolute():
            resolved = raw_path.resolve()
        else:
            resolved = (self.workspace_dir / raw_path).resolve()

        # Check if resolved path is within any allowed directory
        is_safe = False
        for allowed in self.allowed_dirs:
            try:
                resolved.relative_to(allowed)
                is_safe = True
                break
            except ValueError:
                continue

        if not is_safe:
            raise PermissionError(
                f"Path traversal access denied: '{rel_or_abs_path}' resolves to '{resolved}', "
                f"which is outside approved directories."
            )

        if allow_create_parent:
            resolved.parent.mkdir(parents=True, exist_ok=True)

        return resolved

    def safe_read_file(self, path_str: str, max_chars: int = 50000) -> str:
        """Safely reads a file with sandbox enforcement and length capping."""
        safe_path = self.resolve_safe_path(path_str)
        if not safe_path.exists():
            raise FileNotFoundError(f"File not found: '{path_str}'")
        if not safe_path.is_file():
            raise IsADirectoryError(f"Target is a directory, not a file: '{path_str}'")

        content = safe_path.read_text(encoding="utf-8", errors="replace")
        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n... [Truncated {len(content) - max_chars} characters]"
        return content

    def safe_write_file(self, path_str: str, content: str) -> Dict[str, Any]:
        """Safely writes content within the sandboxed directory."""
        safe_path = self.resolve_safe_path(path_str, allow_create_parent=True)
        safe_path.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": str(safe_path),
            "bytes_written": len(content.encode("utf-8")),
            "char_count": len(content)
        }

    # -------------------------------------------------------------------------
    # Secret Redaction
    # -------------------------------------------------------------------------
    def redact_secrets(self, text: str) -> str:
        """Replaces known API keys and secret patterns with '[REDACTED]'."""
        if not text:
            return text

        redacted = text
        for secret in self.known_secrets:
            if secret in redacted:
                redacted = redacted.replace(secret, "[REDACTED]")

        # Pattern 1: raw sk- keys
        redacted = re.sub(r"sk-[a-zA-Z0-9_\-]{20,}", "[REDACTED]", redacted, flags=re.IGNORECASE)

        # Pattern 2: key-value pairs (preserves key label, redacts value)
        redacted = re.sub(
            r"(api[_\-]?key|auth[_\-]?token|secret|password|bearer\s+)[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{12,})['\"]?",
            r"\1: [REDACTED]",
            redacted,
            flags=re.IGNORECASE
        )

        return redacted

    # -------------------------------------------------------------------------
    # Sanitized Environment
    # -------------------------------------------------------------------------
    def get_minimal_env(self, custom_vars: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Creates a clean environment stripped of API keys, tokens, and secrets.
        """
        minimal = {}
        for var_name, var_val in os.environ.items():
            if var_name.upper() in SAFE_ENV_VARS:
                minimal[var_name] = var_val

        # Add python UTF-8 and basic path variables
        minimal["PYTHONIOENCODING"] = "utf-8"
        minimal["PYTHONUTF8"] = "1"

        if custom_vars:
            for k, v in custom_vars.items():
                if not any(term in k.upper() for term in ["KEY", "TOKEN", "SECRET", "PASS"]):
                    minimal[k] = v

        return minimal

    # -------------------------------------------------------------------------
    # Process Tree Termination
    # -------------------------------------------------------------------------
    def kill_process_tree(self, pid: int):
        """
        Terminates the given process and ALL its child/descendant processes.
        """
        if psutil:
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.kill()
                    except Exception:
                        pass
                parent.kill()
            except Exception:
                pass

        # Robust Windows fallback: taskkill.exe /F /T /PID
        if sys.platform == "win32":
            try:
                subprocess.run(
                    ["taskkill.exe", "/F", "/T", "/PID", str(pid)],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Structured Execution
    # -------------------------------------------------------------------------
    def execute_structured(
        self,
        executable: str,
        args: List[str],
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        task_id: Optional[str] = None,
        env_overrides: Optional[Dict[str, str]] = None
    ) -> StructuredExecutionResult:
        """
        Executes a binary with explicit argument array (no raw shell parsing).
        """
        command_id = f"cmd-{uuid.uuid4().hex[:10]}"
        target_timeout = timeout or self.default_timeout

        target_cwd = self.resolve_safe_path(cwd) if cwd else self.workspace_dir
        cmd_list = [executable] + args

        # Build redacted display command
        cmd_display = self.redact_secrets(" ".join(cmd_list))

        self._notify_listeners({
            "type": "command_start",
            "command_id": command_id,
            "task_id": task_id,
            "command": cmd_display,
            "cwd": str(target_cwd),
            "timestamp": time.time()
        })

        clean_env = self.get_minimal_env(env_overrides)
        start_time = time.time()
        timed_out = False
        cancelled = False
        stdout_raw = ""
        stderr_raw = ""
        exit_code = 1

        try:
            process = subprocess.Popen(
                cmd_list,
                cwd=str(target_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=clean_env,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            with self._lock:
                self._active_processes[command_id] = process
                if task_id:
                    self._active_tasks.setdefault(task_id, set()).add(command_id)

            try:
                stdout_raw, stderr_raw = process.communicate(timeout=target_timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                self.kill_process_tree(process.pid)
                stdout_raw, stderr_raw = process.communicate()
                exit_code = -1
                stderr_raw += f"\n[ExecutionBoundary Timeout: Command exceeded {target_timeout}s]"

        except Exception as e:
            exit_code = 1
            stderr_raw = f"[ExecutionBoundary Error: {str(e)}]"
        finally:
            with self._lock:
                self._active_processes.pop(command_id, None)
                if task_id and task_id in self._active_tasks:
                    self._active_tasks[task_id].discard(command_id)

        duration = round(time.time() - start_time, 3)

        # Output capping & secret redaction
        stdout_clean = self.redact_secrets(stdout_raw.strip())
        stderr_clean = self.redact_secrets(stderr_raw.strip())

        truncated = False
        if len(stdout_clean) > self.max_output_chars:
            stdout_clean = stdout_clean[:self.max_output_chars] + f"\n\n[Output truncated at {self.max_output_chars} characters]"
            truncated = True

        combined_output = stdout_clean if stdout_clean else stderr_clean

        res = StructuredExecutionResult(
            command_id=command_id,
            task_id=task_id,
            executable=executable,
            args=args,
            cwd=str(target_cwd),
            exit_code=exit_code,
            duration=duration,
            timed_out=timed_out,
            cancelled=cancelled,
            stdout=stdout_clean,
            stderr=stderr_clean,
            output=combined_output,
            truncated=truncated,
            timestamp=start_time
        )

        self._notify_listeners({
            "type": "command_finish",
            **res.to_dict()
        })

        return res

    def execute_command(
        self,
        command: str,
        shell_type: str = "powershell",
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        task_id: Optional[str] = None
    ) -> StructuredExecutionResult:
        """
        Executes a shell command via PowerShell or CMD while enforcing boundary rules.
        """
        # Block dangerous commands
        for pattern in BLOCKED_COMMAND_PATTERNS:
            if pattern.search(command):
                blocked_id = f"cmd-blocked-{uuid.uuid4().hex[:6]}"
                msg = f"Security Exception: Command '{command}' is blocked by safety guardrails."
                return StructuredExecutionResult(
                    command_id=blocked_id,
                    task_id=task_id,
                    executable="blocked",
                    args=[],
                    cwd=str(self.workspace_dir),
                    exit_code=1,
                    duration=0.0,
                    timed_out=False,
                    cancelled=False,
                    stdout="",
                    stderr=msg,
                    output=msg
                )

        if shell_type.lower() == "powershell":
            executable = "powershell.exe"
            args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-NonInteractive", "-Command", command]
        else:
            executable = "cmd.exe"
            args = ["/c", command]

        return self.execute_structured(
            executable=executable,
            args=args,
            cwd=cwd,
            timeout=timeout,
            task_id=task_id
        )

    # -------------------------------------------------------------------------
    # Cancellation
    # -------------------------------------------------------------------------
    def cancel_command(self, command_id: str) -> bool:
        """Cancels a running command by ID."""
        with self._lock:
            process = self._active_processes.get(command_id)
        if process and process.poll() is None:
            self.kill_process_tree(process.pid)
            return True
        return False

    def cancel_task_processes(self, task_id: str) -> int:
        """Cancels all active processes associated with a task ID."""
        with self._lock:
            cmd_ids = list(self._active_tasks.get(task_id, set()))
        cancelled_count = 0
        for cid in cmd_ids:
            if self.cancel_command(cid):
                cancelled_count += 1
        return cancelled_count
