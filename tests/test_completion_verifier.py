"""
Negative and Positive Tests for CompletionVerifier (Phase 4)
Proves that:
1. Fake completion text without artifacts -> REJECTED
2. Zero-test runs -> REJECTED
3. Failing checks -> REJECTED
4. Missing or empty artifacts -> REJECTED
5. Stale evidence (modified file after test) -> REJECTED
6. Valid task with real passing tests, clean artifacts -> APPROVED
"""
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.verification.completion_verifier import CompletionVerifier
from core.security.execution_boundary import ExecutionBoundary

class TestCompletionVerifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_verif_")
        self.sandbox = Path(self.test_dir).resolve()
        self.boundary = ExecutionBoundary(workspace_dir=self.sandbox)
        self.verifier = CompletionVerifier(self.sandbox, self.boundary)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_negative_fake_completion_without_reviewer(self):
        """Agents emitting completion without Reviewer recommendation must be rejected."""
        res = self.verifier.verify_completion(
            reviewer_messages=["I think this looks good.", "Proceeding to next step."],
            expected_artifacts=None
        )
        self.assertFalse(res.passed)
        self.assertFalse(res.reviewer_recommended)
        self.assertTrue(any("Reviewer has not recommended completion" in r for r in res.rejection_reasons))

    def test_negative_missing_or_empty_artifact(self):
        """Tasks with missing or 0-byte expected artifacts must be rejected."""
        # Create an empty file
        empty_art = self.sandbox / "empty.txt"
        empty_art.touch()

        res = self.verifier.verify_completion(
            reviewer_messages=["Reviewer: Everything passes. TASK_COMPLETED"],
            expected_artifacts=["missing.txt", "empty.txt"]
        )
        self.assertFalse(res.passed)
        self.assertEqual(len(res.missing_artifacts), 2)
        self.assertTrue(any("missing" in r for r in res.rejection_reasons))
        self.assertTrue(any("empty" in r for r in res.rejection_reasons))

    def test_negative_zero_test_run(self):
        """Zero collected tests must NOT be permitted to claim success."""
        # Script that prints OK but ran 0 tests
        script = self.sandbox / "test_dummy.py"
        script.write_text("print('Ran 0 tests in 0.001s\\n\\nOK')", encoding="utf-8")

        res = self.verifier.verify_completion(
            reviewer_messages=["Reviewer: TASK_COMPLETED"],
            test_command=f"python test_dummy.py"
        )
        self.assertFalse(res.passed)
        self.assertTrue(any("Zero tests were collected" in r for r in res.rejection_reasons))

    def test_negative_failing_acceptance_test(self):
        """Acceptance test failures must reject completion."""
        script = self.sandbox / "test_fail.py"
        script.write_text("""
import sys
print("Ran 3 tests in 0.01s")
print("FAILED (failures=1)")
sys.exit(1)
""", encoding="utf-8")

        res = self.verifier.verify_completion(
            reviewer_messages=["Reviewer: TASK_COMPLETED"],
            test_command=f"python test_fail.py"
        )
        self.assertFalse(res.passed)
        self.assertTrue(any("Acceptance test command failed" in r for r in res.rejection_reasons))

    def test_negative_stale_evidence_after_modification(self):
        """Files modified after verification must invalidate completion."""
        code_file = self.sandbox / "module.py"
        code_file.write_text("def solve(): return 42\n", encoding="utf-8")

        # Record hash at time T0
        hash_t0 = self.verifier.compute_file_hash("module.py")

        # Modify file at time T1 (tampered after test)
        code_file.write_text("def solve(): return 999  # Tampered\n", encoding="utf-8")

        res = self.verifier.verify_completion(
            reviewer_messages=["Reviewer: TASK_COMPLETED"],
            expected_artifacts=["module.py"],
            verified_hashes={"module.py": hash_t0}
        )
        self.assertFalse(res.passed)
        self.assertIn("module.py", res.stale_files)
        self.assertTrue(any("Stale verification" in r for r in res.rejection_reasons))

    def test_positive_genuine_completion(self):
        """Real passing tests, non-empty artifacts, and reviewer recommendation passes."""
        # Create genuine artifact
        code_file = self.sandbox / "app.py"
        code_file.write_text("def hello(): return 'world'\n", encoding="utf-8")

        # Create genuine passing test
        test_file = self.sandbox / "test_app.py"
        test_file.write_text("""
print("Ran 2 tests in 0.005s")
print("OK")
""", encoding="utf-8")

        res = self.verifier.verify_completion(
            reviewer_messages=["Reviewer: TASK_COMPLETED. All requirements met."],
            expected_artifacts=["app.py"],
            test_command="python test_app.py"
        )
        self.assertTrue(res.passed, f"Expected pass but failed with: {res.rejection_reasons}")
        self.assertEqual(len(res.artifacts_verified), 1)
        self.assertEqual(res.test_results["passed"], 2)

if __name__ == "__main__":
    unittest.main()
