"""
Git & Repository Skill
Provides agents with controlled Git operations for cloning, status, diffing,
branching, and committing work inside the workspace.
"""
import subprocess
from pathlib import Path
from typing import Dict, Any

class GitSkill:
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path).resolve()

    def run_git(self, args: list, cwd: Path = None) -> Dict[str, Any]:
        """Runs a git command safely."""
        target_cwd = cwd or self.workspace
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=str(target_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "command": f"git {' '.join(args)}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def clone(self, repo_url: str, dest_folder: str = "") -> Dict[str, Any]:
        """Clones a GitHub or remote repository into the workspace."""
        args = ["clone", repo_url]
        if dest_folder:
            args.append(dest_folder)
        return self.run_git(args)

    def status(self) -> Dict[str, Any]:
        """Returns the current git status."""
        return self.run_git(["status", "--short"])

    def diff(self) -> Dict[str, Any]:
        """Returns the current git diff."""
        return self.run_git(["diff"])

    def commit(self, message: str) -> Dict[str, Any]:
        """Stages all changes and creates a commit with the specified message."""
        add_res = self.run_git(["add", "-A"])
        if not add_res["success"]:
            return add_res
        return self.run_git(["commit", "-m", message])
