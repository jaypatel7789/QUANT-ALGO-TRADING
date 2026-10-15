"""
Graphify Skill - Codebase Knowledge Graph & AST Inspector
Enables agents to query codebase structure, dependencies, and symbols
without wasting tokens reading raw files or grepping blindly.
"""
import os
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class GraphifySkill:
    """
    Integrates Graphify knowledge graph capabilities with fallback
    Python AST & relationship parsing for local codebases.
    """
    def __init__(self, default_workspace: str):
        self.workspace = Path(default_workspace).resolve()
        self.graph_cache: Dict[str, Any] = {}

    def index_codebase(self, target_dir: str = None) -> Dict[str, Any]:
        """
        Indexes the target directory into a knowledge graph.
        Analyzes files, functions, classes, imports, and calls.
        """
        scan_dir = Path(target_dir).resolve() if target_dir else self.workspace
        if not scan_dir.exists():
            return {"status": "error", "message": f"Path '{scan_dir}' does not exist"}

        # Attempt to run official graphify CLI if present
        cli_result = self._try_run_graphify_cli(str(scan_dir))
        if cli_result.get("success"):
            return {
                "status": "indexed_with_cli",
                "output": cli_result.get("output"),
                "path": str(scan_dir)
            }

        # Local AST & Structural Parser
        nodes = []
        edges = []
        summary = {"files": 0, "classes": 0, "functions": 0, "imports": 0}

        for path in scan_dir.rglob("*.py"):
            # Skip virtual environments and hidden folders
            if any(part.startswith(".") or part in ["venv", "node_modules", "__pycache__"] for part in path.parts):
                continue

            rel_path = str(path.relative_to(scan_dir))
            summary["files"] += 1
            file_node = {"id": rel_path, "type": "file", "name": path.name}
            nodes.append(file_node)

            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content, filename=str(path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        summary["classes"] += 1
                        class_id = f"{rel_path}::{node.name}"
                        nodes.append({"id": class_id, "type": "class", "name": node.name, "file": rel_path, "line": node.lineno})
                        edges.append({"source": rel_path, "target": class_id, "relation": "defines"})
                    elif isinstance(node, ast.FunctionDef):
                        summary["functions"] += 1
                        func_id = f"{rel_path}::{node.name}"
                        nodes.append({"id": func_id, "type": "function", "name": node.name, "file": rel_path, "line": node.lineno})
                        edges.append({"source": rel_path, "target": func_id, "relation": "defines"})
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            summary["imports"] += 1
                            edges.append({"source": rel_path, "target": alias.name, "relation": "imports"})
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            summary["imports"] += 1
                            edges.append({"source": rel_path, "target": node.module, "relation": "imports_from"})
            except Exception as e:
                # Malformed file or non-python syntax
                pass

        self.graph_cache = {
            "root": str(scan_dir),
            "summary": summary,
            "nodes": nodes,
            "edges": edges
        }

        return {
            "status": "success",
            "message": f"Indexed {summary['files']} files, {summary['classes']} classes, {summary['functions']} functions",
            "summary": summary,
            "sample_nodes": nodes[:15]
        }

    def query_symbol(self, symbol_name: str) -> Dict[str, Any]:
        """
        Finds a function, class, or module in the indexed knowledge graph.
        """
        if not self.graph_cache:
            self.index_codebase()

        matches = [
            n for n in self.graph_cache.get("nodes", [])
            if symbol_name.lower() in n.get("name", "").lower()
        ]

        related_edges = [
            e for e in self.graph_cache.get("edges", [])
            if any(m["id"] in [e.get("source"), e.get("target")] for m in matches)
        ]

        return {
            "query": symbol_name,
            "matched_symbols": matches,
            "relationships": related_edges[:20]
        }

    def _try_run_graphify_cli(self, path_str: str) -> Dict[str, Any]:
        """Tries executing installed graphify command."""
        for cmd in ["graphify", "graphifyy"]:
            try:
                res = subprocess.run(
                    [cmd, "--help"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3
                )
                if res.returncode == 0:
                    run_res = subprocess.run(
                        [cmd, "index", path_str],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=30
                    )
                    return {"success": True, "output": run_res.stdout}
            except Exception:
                continue
        return {"success": False}
