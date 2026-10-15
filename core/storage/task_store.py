"""
Durable Task Persistence & State Machine (Phase 3)
SQLite-backed durable store providing:
- Task lifecycle tracking (queued, running, waiting, reviewing, succeeded, failed, cancelled)
- Atomic concurrency-safe task claiming
- Duplicate dispatch protection via idempotency keys
- Restart recovery of interrupted tasks
- Sequential event logging for reconnecting dashboard clients
- Artifact tracking with content hashes
- Operation reconciliation to avoid repeating side effects
"""
import os
import sys
import time
import json
import sqlite3
import hashlib
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

# Valid State Transitions Table
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    "queued": {"running", "cancelled"},
    "running": {"waiting", "reviewing", "failed", "cancelled"},
    "waiting": {"running", "failed", "cancelled"},
    "reviewing": {"succeeded", "running", "failed", "cancelled"},
    "failed": {"queued", "failed"},  # Can transition back to queued on retry
    "succeeded": set(),               # Terminal state
    "cancelled": set()                # Terminal state
}

class TaskStore:
    """
    SQLite-backed durable task manager and event store.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path).resolve()
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = base_dir / "tasks.sqlite3"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        """Initializes database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                parent_id TEXT NULL,
                dependencies TEXT NOT NULL DEFAULT '[]',
                prompt TEXT NOT NULL,
                acceptance_criteria TEXT NOT NULL DEFAULT '[]',
                assigned_role TEXT NOT NULL DEFAULT 'Engineer',
                selected_model TEXT NOT NULL DEFAULT 'primary',
                status TEXT NOT NULL DEFAULT 'queued',
                attempt_count INTEGER NOT NULL DEFAULT 0,
                max_attempts INTEGER NOT NULL DEFAULT 3,
                created_at REAL NOT NULL,
                started_at REAL NULL,
                completed_at REAL NULL,
                deadline REAL NULL,
                budget_tokens INTEGER NOT NULL DEFAULT 100000,
                tokens_used INTEGER NOT NULL DEFAULT 0,
                workspace_dir TEXT NOT NULL,
                code_revision TEXT NOT NULL DEFAULT 'HEAD',
                verification_results TEXT NOT NULL DEFAULT '{}',
                failure_reasons TEXT NOT NULL DEFAULT '[]',
                idempotency_key TEXT UNIQUE NULL
            );

            CREATE TABLE IF NOT EXISTS task_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                type TEXT NOT NULL,
                sender TEXT NOT NULL DEFAULT 'System',
                content TEXT NOT NULL DEFAULT '',
                data TEXT NOT NULL DEFAULT '{}',
                timestamp REAL NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS task_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                rel_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS operation_logs (
                op_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                parameters TEXT NOT NULL DEFAULT '{}',
                result TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending',
                timestamp REAL NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_task_events_seq ON task_events(event_id);
            CREATE INDEX IF NOT EXISTS idx_task_events_task ON task_events(task_id);
            """)

    # -------------------------------------------------------------------------
    # Task Lifecycle Management
    # -------------------------------------------------------------------------
    def create_task(
        self,
        prompt: str,
        workspace_dir: str,
        parent_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        acceptance_criteria: Optional[List[str]] = None,
        assigned_role: str = "Engineer",
        selected_model: str = "primary",
        max_attempts: int = 3,
        deadline: Optional[float] = None,
        budget_tokens: int = 100000,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a new task. If an identical active task exists with the same
        idempotency key, returns the existing task (duplicate dispatch protection).
        """
        # Generate idempotency key if not given
        if not idempotency_key:
            hash_input = f"{prompt.strip()}|{json.dumps(acceptance_criteria or [])}"
            idempotency_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        with self._get_connection() as conn:
            # Check existing task with same key
            cur = conn.execute("SELECT * FROM tasks WHERE idempotency_key = ?", (idempotency_key,))
            existing = cur.fetchone()
            if existing:
                row_dict = dict(existing)
                # If existing is already queued or running, return it directly
                if row_dict["status"] in ["queued", "running", "waiting", "reviewing"]:
                    return row_dict

            task_id = f"task-{uuid.uuid4().hex[:12]}"
            now = time.time()

            conn.execute("""
                INSERT INTO tasks (
                    id, parent_id, dependencies, prompt, acceptance_criteria,
                    assigned_role, selected_model, status, attempt_count, max_attempts,
                    created_at, deadline, budget_tokens, workspace_dir, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                parent_id,
                json.dumps(dependencies or []),
                prompt,
                json.dumps(acceptance_criteria or []),
                assigned_role,
                selected_model,
                max_attempts,
                now,
                deadline,
                budget_tokens,
                workspace_dir,
                idempotency_key
            ))

            self.log_event(
                task_id=task_id,
                event_type="task_created",
                sender="System",
                content=f"Task {task_id} queued.",
                data={"prompt": prompt, "assigned_role": assigned_role},
                conn=conn
            )

        return self.get_task(task_id)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Fetches task details by ID."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            if not row:
                return None
            res = dict(row)
            res["dependencies"] = json.loads(res["dependencies"])
            res["acceptance_criteria"] = json.loads(res["acceptance_criteria"])
            res["verification_results"] = json.loads(res["verification_results"])
            res["failure_reasons"] = json.loads(res["failure_reasons"])
            return res

    def list_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent tasks ordered by creation time descending."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            results = []
            for r in rows:
                res = dict(r)
                try:
                    res["dependencies"] = json.loads(res["dependencies"])
                    res["acceptance_criteria"] = json.loads(res["acceptance_criteria"])
                    res["verification_results"] = json.loads(res["verification_results"])
                    res["failure_reasons"] = json.loads(res["failure_reasons"])
                except Exception:
                    pass
                results.append(res)
            return results

    def claim_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Concurrency-safe atomic claim of the next queued task.
        """
        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE;")
            cur = conn.execute("""
                SELECT id FROM tasks 
                WHERE status = 'queued' 
                ORDER BY created_at ASC 
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                conn.commit()
                return None

            task_id = row["id"]
            now = time.time()
            conn.execute("""
                UPDATE tasks 
                SET status = 'running',
                    started_at = COALESCE(started_at, ?),
                    attempt_count = attempt_count + 1
                WHERE id = ? AND status = 'queued'
            """, (now, task_id))
            conn.commit()

        self.log_event(
            task_id=task_id,
            event_type="task_claimed",
            sender="System",
            content=f"Task {task_id} claimed and transitioned to running."
        )
        return self.get_task(task_id)

    def transition_status(
        self,
        task_id: str,
        new_status: str,
        verification_results: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transitions task status with state machine validation.
        """
        if new_status not in VALID_TRANSITIONS:
            raise ValueError(f"Invalid status: '{new_status}'")

        with self._get_connection() as conn:
            cur = conn.execute("SELECT status, failure_reasons FROM tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            if not row:
                raise KeyError(f"Task '{task_id}' not found.")

            current_status = row["status"]
            allowed = VALID_TRANSITIONS.get(current_status, set())
            if new_status not in allowed:
                raise ValueError(
                    f"Illegal state transition for task {task_id}: '{current_status}' -> '{new_status}'. "
                    f"Allowed transitions: {allowed}"
                )

            reasons = json.loads(row["failure_reasons"])
            if failure_reason:
                reasons.append({"timestamp": time.time(), "reason": failure_reason})

            now = time.time()
            completed_at = now if new_status in ["succeeded", "failed", "cancelled"] else None

            conn.execute("""
                UPDATE tasks 
                SET status = ?,
                    completed_at = COALESCE(?, completed_at),
                    verification_results = COALESCE(?, verification_results),
                    failure_reasons = ?
                WHERE id = ?
            """, (
                new_status,
                completed_at,
                json.dumps(verification_results) if verification_results else None,
                json.dumps(reasons),
                task_id
            ))

        self.log_event(
            task_id=task_id,
            event_type=f"task_{new_status}",
            sender="System",
            content=f"Task {task_id} transitioned from '{current_status}' to '{new_status}'.",
            data={
                "previous_status": current_status,
                "new_status": new_status,
                "failure_reason": failure_reason,
                "verification_results": verification_results
            }
        )

        return self.get_task(task_id)

    # -------------------------------------------------------------------------
    # Event Stream & Sequential Logging
    # -------------------------------------------------------------------------
    def log_event(
        self,
        task_id: str,
        event_type: str,
        sender: str = "System",
        content: str = "",
        data: Optional[Dict[str, Any]] = None,
        conn: Optional[sqlite3.Connection] = None
    ) -> int:
        """Appends an event to the sequential log and returns the event_id."""
        now = time.time()
        payload = json.dumps(data or {})
        if conn is not None:
            cur = conn.execute("""
                INSERT INTO task_events (task_id, type, sender, content, data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (task_id, event_type, sender, content, payload, now))
            return cur.lastrowid

        with self._get_connection() as c:
            cur = c.execute("""
                INSERT INTO task_events (task_id, type, sender, content, data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (task_id, event_type, sender, content, payload, now))
            return cur.lastrowid

    def get_events(
        self,
        task_id: Optional[str] = None,
        since_event_id: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieves ordered events starting after `since_event_id`
        (supports reconnecting dashboard clients recovering missed messages).
        """
        with self._get_connection() as conn:
            if task_id:
                cur = conn.execute("""
                    SELECT * FROM task_events 
                    WHERE task_id = ? AND event_id > ?
                    ORDER BY event_id ASC LIMIT ?
                """, (task_id, since_event_id, limit))
            else:
                cur = conn.execute("""
                    SELECT * FROM task_events 
                    WHERE event_id > ?
                    ORDER BY event_id ASC LIMIT ?
                """, (since_event_id, limit))

            rows = cur.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["data"] = json.loads(d["data"])
                results.append(d)
            return results

    # -------------------------------------------------------------------------
    # Artifact Tracking
    # -------------------------------------------------------------------------
    def register_artifact(self, task_id: str, rel_path: str, abs_path: Path) -> Dict[str, Any]:
        """Calculates content SHA256 and records task artifact."""
        if not abs_path.exists():
            raise FileNotFoundError(f"Artifact not found: {abs_path}")

        content_bytes = abs_path.read_bytes()
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        size_bytes = len(content_bytes)
        now = time.time()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO task_artifacts (task_id, rel_path, content_hash, size_bytes, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, rel_path, content_hash, size_bytes, now))

        self.log_event(
            task_id=task_id,
            event_type="artifact_generated",
            sender="System",
            content=f"Artifact created: {rel_path} ({size_bytes} bytes)",
            data={"rel_path": rel_path, "sha256": content_hash, "size": size_bytes}
        )

        return {
            "task_id": task_id,
            "rel_path": rel_path,
            "content_hash": content_hash,
            "size_bytes": size_bytes
        }

    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns all recorded artifacts for a task."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM task_artifacts WHERE task_id = ? ORDER BY id ASC", (task_id,))
            return [dict(r) for r in cur.fetchall()]

    # -------------------------------------------------------------------------
    # Restart Recovery & Operation Reconciliation
    # -------------------------------------------------------------------------
    def recover_interrupted_tasks(self) -> List[Dict[str, Any]]:
        """
        Scans for tasks left in 'running' or 'reviewing' state across restarts.
        Marks them as interrupted and resets to queued if attempts < max_attempts.
        """
        recovered = []
        with self._get_connection() as conn:
            cur = conn.execute("""
                SELECT id, attempt_count, max_attempts, status 
                FROM tasks 
                WHERE status IN ('running', 'reviewing')
            """)
            stuck_tasks = cur.fetchall()

            for t in stuck_tasks:
                task_id = t["id"]
                attempts = t["attempt_count"]
                max_att = t["max_attempts"]

                if attempts < max_att:
                    new_status = "queued"
                    reason = f"System restarted while task was in '{t['status']}' (attempt {attempts}/{max_att}). Re-queued."
                else:
                    new_status = "failed"
                    reason = f"Task interrupted and exceeded max attempts ({attempts}/{max_att})."

                conn.execute("""
                    UPDATE tasks 
                    SET status = ? 
                    WHERE id = ?
                """, (new_status, task_id))

                self.log_event(
                    task_id=task_id,
                    event_type="task_recovered",
                    sender="System",
                    content=reason,
                    data={"previous_status": t["status"], "new_status": new_status},
                    conn=conn
                )
                recovered.append({"task_id": task_id, "action": new_status, "reason": reason})

        return recovered

    # -------------------------------------------------------------------------
    # Side-Effect Operation Logging
    # -------------------------------------------------------------------------
    def record_operation_start(
        self,
        op_id: str,
        task_id: str,
        op_type: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Records an operation ID before side effects execute to prevent duplicate replays.
        """
        now = time.time()
        with self._get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO operation_logs (op_id, task_id, operation_type, parameters, status, timestamp)
                    VALUES (?, ?, ?, ?, 'pending', ?)
                """, (op_id, task_id, op_type, json.dumps(parameters), now))
                return True
            except sqlite3.IntegrityError:
                # Operation already recorded
                return False

    def complete_operation(
        self,
        op_id: str,
        result: Dict[str, Any],
        success: bool = True
    ):
        """Marks a recorded operation as completed."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE operation_logs 
                SET result = ?, status = ? 
                WHERE op_id = ?
            """, (json.dumps(result), "completed" if success else "failed", op_id))

    def clear_all(self):
        """Wipes all tasks, events, artifacts, and operation logs for a clean reset."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM task_events;")
            conn.execute("DELETE FROM task_artifacts;")
            conn.execute("DELETE FROM operation_logs;")
            conn.execute("DELETE FROM tasks;")

    def delete_task(self, task_id: str) -> bool:
        """Deletes a specific task and cascades to its events."""
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cur.rowcount > 0

