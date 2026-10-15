"""
System & File Skill
Allows agents to inspect system resources, search directories, read files,
and write files strictly within the designated sandboxed workspace.
"""
import os
import platform
import psutil
from pathlib import Path
from typing import Dict, Any, List

from core.security.execution_boundary import ExecutionBoundary

class SystemSkill:
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path).resolve()
        self.boundary = ExecutionBoundary(self.workspace)

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Returns CPU, RAM, Disk, and OS metrics."""
        return {
            "os": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "workspace": str(self.workspace)
        }

    def list_files(self, subfolder: str = "") -> List[Dict[str, Any]]:
        """Lists files and folders inside the workspace with traversal checks."""
        try:
            target = self.boundary.resolve_safe_path(subfolder)
        except PermissionError:
            return []

        if not target.exists() or not target.is_dir():
            return []

        results = []
        for item in target.iterdir():
            results.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else None
            })
        return results

    def read_file(self, rel_path: str, max_chars: int = 10000) -> str:
        """Reads content from a file inside the workspace safely."""
        try:
            return self.boundary.safe_read_file(rel_path, max_chars=max_chars)
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, rel_path: str, content: str) -> str:
        """Writes content to a file inside the workspace safely."""
        try:
            res = self.boundary.safe_write_file(rel_path, content)
            return f"Successfully wrote {res['char_count']} characters to {rel_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
