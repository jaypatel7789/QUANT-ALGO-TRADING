"""
Unit Tests for Durable Task Persistence & State Machine (Phase 3)
Using Python standard library unittest.
"""
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.storage.task_store import TaskStore

class TestTaskStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_store_")
        self.db_path = Path(self.test_dir) / "test_tasks.sqlite3"
        self.store = TaskStore(str(self.db_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_task_creation_and_retrieval(self):
        task = self.store.create_task(
            prompt="Build test endpoint",
            workspace_dir=self.test_dir,
            acceptance_criteria=["Return status 200", "Include valid JSON"]
        )
        self.assertEqual(task["status"], "queued")
        self.assertEqual(task["prompt"], "Build test endpoint")
        self.assertEqual(len(task["acceptance_criteria"]), 2)

    def test_duplicate_dispatch_protection(self):
        t1 = self.store.create_task(
            prompt="Identical Prompt",
            workspace_dir=self.test_dir,
            acceptance_criteria=["Criterion 1"]
        )
        # Dispatch again while queued
        t2 = self.store.create_task(
            prompt="Identical Prompt",
            workspace_dir=self.test_dir,
            acceptance_criteria=["Criterion 1"]
        )
        self.assertEqual(t1["id"], t2["id"], "Duplicate dispatch must return the existing active task")

    def test_atomic_claiming(self):
        t1 = self.store.create_task(prompt="Task 1", workspace_dir=self.test_dir)
        claimed = self.store.claim_next_task()
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], t1["id"])
        self.assertEqual(claimed["status"], "running")
        self.assertEqual(claimed["attempt_count"], 1)

        # Claiming again when queue is empty returns None
        claimed_empty = self.store.claim_next_task()
        self.assertIsNone(claimed_empty)

    def test_valid_state_transitions(self):
        t = self.store.create_task(prompt="Lifecycle Task", workspace_dir=self.test_dir)
        tid = t["id"]

        # queued -> running
        t_run = self.store.transition_status(tid, "running")
        self.assertEqual(t_run["status"], "running")

        # running -> reviewing
        t_rev = self.store.transition_status(tid, "reviewing")
        self.assertEqual(t_rev["status"], "reviewing")

        # reviewing -> succeeded
        t_suc = self.store.transition_status(tid, "succeeded", verification_results={"tests": "passed"})
        self.assertEqual(t_suc["status"], "succeeded")
        self.assertIsNotNone(t_suc["completed_at"])

    def test_invalid_state_transition_rejection(self):
        t = self.store.create_task(prompt="Invalid Transition Task", workspace_dir=self.test_dir)
        tid = t["id"]

        # queued -> succeeded is illegal (must go through running/reviewing)
        with self.assertRaises(ValueError):
            self.store.transition_status(tid, "succeeded")

        # transition to running, then succeeded, then try to transition back to queued
        self.store.transition_status(tid, "running")
        self.store.transition_status(tid, "reviewing")
        self.store.transition_status(tid, "succeeded")

        with self.assertRaises(ValueError):
            self.store.transition_status(tid, "queued")

    def test_restart_recovery(self):
        t1 = self.store.create_task(prompt="Interrupted Task", workspace_dir=self.test_dir, max_attempts=3)
        self.store.transition_status(t1["id"], "running")

        # Simulate system crash and reboot
        recovered = self.store.recover_interrupted_tasks()
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0]["action"], "queued")

        refreshed = self.store.get_task(t1["id"])
        self.assertEqual(refreshed["status"], "queued")

    def test_sequential_event_logging(self):
        t = self.store.create_task(prompt="Event Task", workspace_dir=self.test_dir)
        e1 = self.store.log_event(t["id"], "step_1", content="Step 1 details")
        e2 = self.store.log_event(t["id"], "step_2", content="Step 2 details")
        self.assertGreater(e2, e1)

        # Retrieve events after e1
        missed = self.store.get_events(task_id=t["id"], since_event_id=e1)
        self.assertEqual(len(missed), 1)
        self.assertEqual(missed[0]["type"], "step_2")

    def test_list_tasks(self):
        self.store.create_task(prompt="Task 1", workspace_dir=self.test_dir)
        self.store.create_task(prompt="Task 2", workspace_dir=self.test_dir)
        tasks = self.store.list_tasks(limit=10)
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["prompt"], "Task 2")
        self.assertEqual(tasks[1]["prompt"], "Task 1")

if __name__ == "__main__":
    unittest.main()
