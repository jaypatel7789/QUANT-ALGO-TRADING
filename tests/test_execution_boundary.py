"""
Unit Tests for ExecutionBoundary & Sandboxing (Phase 2)
Using Python standard library unittest.
"""
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure root is in path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.security.execution_boundary import ExecutionBoundary, StructuredExecutionResult
from core.executor import WindowsSystemExecutor

class TestExecutionBoundary(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_sandbox_")
        self.sandbox = Path(self.test_dir).resolve()
        self.boundary = ExecutionBoundary(workspace_dir=self.sandbox)
        self.executor = WindowsSystemExecutor(str(self.sandbox))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_path_traversal_rejection(self):
        # Valid relative path inside sandbox
        safe_path = self.boundary.resolve_safe_path("sub/file.txt")
        self.assertTrue(str(safe_path).startswith(str(self.sandbox)))

        # Traversal attack attempting to escape sandbox
        with self.assertRaises(PermissionError):
            self.boundary.resolve_safe_path("../outside.txt")

        # Windows root escape
        with self.assertRaises(PermissionError):
            self.boundary.resolve_safe_path("C:\\Windows\\System32\\calc.exe")

    def test_secret_redaction(self):
        secret_key = "sk-testsecretkey12345678901234567890"
        boundary = ExecutionBoundary(workspace_dir=self.sandbox, known_secrets={secret_key})

        redacted = boundary.redact_secrets(f"Authorization: Bearer {secret_key}")
        self.assertNotIn(secret_key, redacted)
        self.assertIn("[REDACTED]", redacted)

    def test_minimal_env_isolation(self):
        os.environ["SECRET_LEAK_TOKEN"] = "sensitive_token_9999"
        os.environ["OPENAI_API_KEY"] = "sk-leakedkey12345"

        clean_env = self.boundary.get_minimal_env()

        self.assertNotIn("SECRET_LEAK_TOKEN", clean_env)
        self.assertNotIn("OPENAI_API_KEY", clean_env)
        self.assertIn("PATH", clean_env)

    def test_safe_read_write(self):
        # Safe write
        self.boundary.safe_write_file("data/test.txt", "Hello Sandbox!")
        self.assertTrue((self.sandbox / "data" / "test.txt").exists())

        # Safe read
        content = self.boundary.safe_read_file("data/test.txt")
        self.assertEqual(content, "Hello Sandbox!")

        # Traversal read fails
        with self.assertRaises(PermissionError):
            self.boundary.safe_read_file("../../secret.txt")

    def test_structured_execution(self):
        res = self.boundary.execute_structured(
            executable=sys.executable,
            args=["-c", "print('Executed via structured binary!')"]
        )
        self.assertEqual(res.exit_code, 0)
        self.assertIn("Executed via structured binary!", res.stdout)
        self.assertFalse(res.timed_out)

    def test_blocked_dangerous_command(self):
        res = self.executor.execute_command("format C: /fs:NTFS")
        self.assertNotEqual(res["exit_code"], 0)
        self.assertIn("blocked by safety guardrails", res["output"].lower())

    def test_timeout_and_process_kill(self):
        # Script that sleeps for 10 seconds with 1 second timeout
        res = self.boundary.execute_structured(
            executable=sys.executable,
            args=["-c", "import time; time.sleep(10)"],
            timeout=1
        )
        self.assertTrue(res.timed_out)
        self.assertEqual(res.exit_code, -1)

if __name__ == "__main__":
    unittest.main()
