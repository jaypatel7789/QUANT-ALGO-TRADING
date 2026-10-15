"""
Multi-Agent Orchestrator (Phases 3, 4, 5, 7)
Coordinates task execution with:
- Durable SQLite task tracking and state transitions
- Restart recovery of interrupted tasks
- Evidence-based completion verification (gatekeeper)
- Dynamic targeted sub-team activation (minimal agent sets)
- Centralized execution boundary and process cancellation
- Sequential event streaming with replay for dashboard recovery
"""
import sys
import time
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Set

from core.agents.team import AgentTeam
from core.config import WORKSPACE_DIR
from core.brain import MetaBrain
from core.storage.task_store import TaskStore
from core.security.execution_boundary import ExecutionBoundary
from core.verification.completion_verifier import CompletionVerifier
from core.models.model_registry import model_registry

class MultiAgentOrchestrator:
    def __init__(self, workspace_path: Optional[str] = None, db_path: Optional[str] = None):
        self.workspace = Path(workspace_path or WORKSPACE_DIR).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.store = TaskStore(db_path)
        self.boundary = ExecutionBoundary(self.workspace)
        self.verifier = CompletionVerifier(self.workspace, self.boundary)
        self.team = AgentTeam(str(self.workspace))
        self.brain = MetaBrain(str(self.workspace))

        self.listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._lock = threading.Lock()

        # Automatic restart recovery of interrupted tasks on startup
        recovered = self.store.recover_interrupted_tasks()
        if recovered:
            print(f"[Orchestrator] Recovered {len(recovered)} interrupted task(s) from previous run.", file=sys.stderr)

    @property
    def is_running(self) -> bool:
        with self._lock:
            return len(self._running_tasks) > 0

    @property
    def active_task(self) -> Optional[str]:
        with self._lock:
            if self._running_tasks:
                return next(iter(self._running_tasks.keys()))
        return None

    @property
    def history(self) -> List[Dict[str, Any]]:
        with self.store._get_connection() as conn:
            cur = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20")
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def clear_history(self):
        """Wipes durable task store and command execution history."""
        self.store.clear_all()
        if hasattr(self.team, "executor") and hasattr(self.team.executor, "execution_history"):
            self.team.executor.execution_history.clear()
        self.broadcast({"type": "history_cleared", "timestamp": time.time()})


    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers an event listener (e.g. WebSocket broadcaster)."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Unregisters an event listener."""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def broadcast(self, event: Dict[str, Any]):
        """Emits an event payload to all subscribers."""
        event.setdefault("timestamp", time.time())
        for cb in self.listeners:
            try:
                cb(event)
            except Exception as e:
                print(f"[Orchestrator Broadcast Warning] {e}", file=sys.stderr)

    def log_and_broadcast(
        self,
        task_id: str,
        event_type: str,
        sender: str = "System",
        content: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """Persists event to SQLite and broadcasts to connected clients."""
        eid = self.store.log_event(
            task_id=task_id,
            event_type=event_type,
            sender=sender,
            content=content,
            data=data
        )
        self.broadcast({
            "event_id": eid,
            "task_id": task_id,
            "type": event_type,
            "sender": sender,
            "content": content,
            "data": data or {},
            "timestamp": time.time()
        })
        return eid

    async def _execute_task_async(
        self,
        task_id: str,
        task_prompt: str,
        acceptance_criteria: Optional[List[str]] = None,
        expected_artifacts: Optional[List[str]] = None,
        test_command: Optional[str] = None,
        max_turns: int = 20
    ) -> Dict[str, Any]:
        """
        Executes a task through targeted sub-teams, logs events, and runs evidence verification.
        """
        start_time = time.time()
        reviewer_messages: List[str] = []

        with self._lock:
            try:
                cur_task = asyncio.current_task()
                if cur_task:
                    self._running_tasks[task_id] = cur_task
            except Exception:
                pass

        # 1. Meta-Brain Planning & Domain Classification
        brain_plan = self.brain.analyze_and_plan(task_prompt)
        domain = brain_plan.get("classified_domain", "general")
        primary_model = brain_plan.get("allocated_primary_model", "primary")

        # Emit task_started event for live dashboard tracking
        self.log_and_broadcast(
            task_id=task_id,
            event_type="task_started",
            sender="Orchestrator",
            content=f"Mission started: {task_prompt}",
            data={"task": task_prompt, "task_id": task_id, "brain_plan": brain_plan}
        )

        self.log_and_broadcast(
            task_id=task_id,
            event_type="agent_message",
            sender="Brain",
            content=f"🧠 **Meta-Brain Strategy Allocated**\n- **Domain**: `{domain}`\n- **Primary Model**: `{primary_model}`\n- **Recommended Skill**: `{brain_plan.get('recommended_skill')}`\n- **Guidance**: {brain_plan.get('skill_snippet', '')[:200]}...",
            data={"domain": domain, "model": primary_model}
        )

        # 2. Activate Targeted Sub-Team (minimal agents needed)
        targeted_team = self.team.create_targeted_team(task_type=domain, max_turns=max_turns)
        participant_names = [a.name for a in targeted_team._participants]

        self.log_and_broadcast(
            task_id=task_id,
            event_type="team_activated",
            sender="Orchestrator",
            content=f"Activated targeted sub-team: {', '.join(participant_names)} (Tokens and turns optimized)",
            data={"participants": participant_names}
        )

        # 3. Stream Agent Messages
        execution_failed = False
        error_msg = None

        try:
            async for event in targeted_team.run_stream(task=task_prompt):
                source = getattr(event, "source", "Agent")
                content = getattr(event, "content", "")

                if isinstance(content, list):
                    content = " ".join(str(c) for c in content)
                elif hasattr(event, "result") and not content:
                    content = str(getattr(event, "result"))

                if content:
                    clean_content = self.boundary.redact_secrets(str(content))
                    if source == "Reviewer":
                        reviewer_messages.append(clean_content)

                    self.log_and_broadcast(
                        task_id=task_id,
                        event_type="agent_message",
                        sender=source,
                        content=clean_content
                    )

        except asyncio.CancelledError:
            self.store.transition_status(task_id, "cancelled", failure_reason="Task cancelled by user.")
            self.boundary.cancel_task_processes(task_id)
            return {"status": "cancelled", "task_id": task_id}
        except Exception as e:
            execution_failed = True
            error_msg = str(e)
            self.log_and_broadcast(
                task_id=task_id,
                event_type="task_error",
                sender="System",
                content=f"Error during agent loop: {error_msg}"
            )

        # 4. Transition to Reviewing State
        if not execution_failed:
            self.store.transition_status(task_id, "reviewing")

        # 5. Evidence-Based Completion Verification Gatekeeper
        validation = self.verifier.verify_completion(
            reviewer_messages=reviewer_messages,
            expected_artifacts=expected_artifacts,
            test_command=test_command
        )

        duration = round(time.time() - start_time, 2)

        if not execution_failed and validation.passed:
            final_status = "succeeded"
            self.store.transition_status(
                task_id=task_id,
                new_status="succeeded",
                verification_results=validation.to_dict()
            )
            self.log_and_broadcast(
                task_id=task_id,
                event_type="task_completed",
                sender="Verifier",
                content=f"✅ **Task Succeeded**: Evidence verified across {len(validation.artifacts_verified)} artifacts and acceptance tests in {duration}s.",
                data=validation.to_dict()
            )
        else:
            final_status = "failed"
            reasons = validation.rejection_reasons
            if error_msg:
                reasons.append(error_msg)
            failure_str = "; ".join(reasons) if reasons else "Unknown failure"

            self.store.transition_status(
                task_id=task_id,
                new_status="failed",
                verification_results=validation.to_dict(),
                failure_reason=failure_str
            )
            self.log_and_broadcast(
                task_id=task_id,
                event_type="task_failed",
                sender="Verifier",
                content=f"❌ **Task Failed Verification**: {failure_str}",
                data=validation.to_dict()
            )

        with self._lock:
            self._running_tasks.pop(task_id, None)

        self.log_and_broadcast(
            task_id=task_id,
            event_type="task_finished",
            sender="Orchestrator",
            content=f"Mission finished: {final_status} ({duration}s)",
            data={
                "task_id": task_id,
                "status": final_status,
                "duration": duration,
                "message_count": len(reviewer_messages) + 2,
                "verification": validation.to_dict()
            }
        )

        return {
            "task_id": task_id,
            "status": final_status,
            "duration": duration,
            "verification": validation.to_dict()
        }

    async def dispatch_task_async(
        self,
        task_prompt: str,
        max_turns: int = 20,
        acceptance_criteria: Optional[List[str]] = None,
        expected_artifacts: Optional[List[str]] = None,
        test_command: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Asynchronous task dispatcher for native FastAPI and WebSocket streaming.
        """
        # 1. Create or retrieve task in SQLite if not pre-created
        if not task_id:
            task = self.store.create_task(
                prompt=task_prompt,
                workspace_dir=str(self.workspace),
                acceptance_criteria=acceptance_criteria
            )
            task_id = task["id"]

        # 2. Atomically claim task
        claimed = self.store.claim_next_task()
        if not claimed or claimed["id"] != task_id:
            # Check if task is already running
            existing = self.store.get_task(task_id)
            if existing and existing["status"] in ("running", "reviewing"):
                return existing

        # 3. Await native execution without thread or loop conflicts
        return await self._execute_task_async(
            task_id=task_id,
            task_prompt=task_prompt,
            acceptance_criteria=acceptance_criteria,
            expected_artifacts=expected_artifacts,
            test_command=test_command,
            max_turns=max_turns
        )

    def dispatch_task(
        self,
        task_prompt: str,
        max_turns: int = 20,
        acceptance_criteria: Optional[List[str]] = None,
        expected_artifacts: Optional[List[str]] = None,
        test_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for CLI, scripts, and unit tests.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.dispatch_task_async(
                        task_prompt=task_prompt,
                        max_turns=max_turns,
                        acceptance_criteria=acceptance_criteria,
                        expected_artifacts=expected_artifacts,
                        test_command=test_command
                    )).result()
            else:
                return loop.run_until_complete(self.dispatch_task_async(
                    task_prompt=task_prompt,
                    max_turns=max_turns,
                    acceptance_criteria=acceptance_criteria,
                    expected_artifacts=expected_artifacts,
                    test_command=test_command
                ))
        except RuntimeError:
            return asyncio.run(self.dispatch_task_async(
                task_prompt=task_prompt,
                max_turns=max_turns,
                acceptance_criteria=acceptance_criteria,
                expected_artifacts=expected_artifacts,
                test_command=test_command
            ))

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancels an active task and terminates its running Windows process trees.
        """
        with self._lock:
            task_obj = self._running_tasks.get(task_id)
            if task_obj and not task_obj.done():
                task_obj.cancel()

        # Kill any child processes spawned by this task
        killed = self.boundary.cancel_task_processes(task_id)

        try:
            self.store.transition_status(task_id, "cancelled", failure_reason="Cancelled by user command.")
        except Exception:
            pass

        self.log_and_broadcast(
            task_id=task_id,
            event_type="task_cancelled",
            sender="System",
            content=f"Task {task_id} cancelled. Terminated {killed} child process tree(s)."
        )
        return True
