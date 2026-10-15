"""
Evidence-Based Completion Verifier (Phase 4)
Enforces that tasks cannot be marked 'succeeded' merely by an agent emitting text.
Requires verifiable evidence:
- Reviewer recommendation
- Expected artifacts verified (non-empty, valid paths, hashed)
- Acceptance test suite verification (strictly non-zero tests, exit code 0)
- Syntax and compilation verification
- Stale verification invalidation (detects post-test file modifications)
- Advisory bloat scoring (correctness and maintainability take precedence)
"""
import os
import sys
import re
import py_compile
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set

from core.security.execution_boundary import ExecutionBoundary, StructuredExecutionResult
from core.skills.ponytail_rules import audit_code_for_bloat

@dataclass
class EvidenceValidationResult:
    passed: bool
    reviewer_recommended: bool
    artifacts_verified: List[Dict[str, Any]] = field(default_factory=list)
    missing_artifacts: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    syntax_results: Dict[str, Any] = field(default_factory=dict)
    verified_hashes: Dict[str, str] = field(default_factory=dict)
    stale_files: List[str] = field(default_factory=list)
    bloat_advisory: Dict[str, Any] = field(default_factory=dict)
    rejection_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CompletionVerifier:
    """
    Validates task completion against rigorous criteria.
    """
    def __init__(self, workspace_dir: Path, boundary: Optional[ExecutionBoundary] = None):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.boundary = boundary or ExecutionBoundary(self.workspace_dir)

    def compute_file_hash(self, rel_path: str) -> str:
        """Calculates SHA256 hash of a sandboxed file."""
        safe_path = self.boundary.resolve_safe_path(rel_path)
        if not safe_path.exists() or not safe_path.is_file():
            return ""
        return hashlib.sha256(safe_path.read_bytes()).hexdigest()

    def check_stale_evidence(self, recorded_hashes: Dict[str, str]) -> List[str]:
        """
        Detects if any verified files were modified after test/review verification.
        """
        stale = []
        for rel_path, expected_hash in recorded_hashes.items():
            current_hash = self.compute_file_hash(rel_path)
            if current_hash != expected_hash:
                stale.append(rel_path)
        return stale

    def parse_test_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """
        Extracts test counts from unittest or pytest console output.
        """
        results = {
            "exit_code": exit_code,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "output_snippet": output[:500] if output else ""
        }

        # Check standard unittest output: "Ran X tests in Ys"
        unittest_match = re.search(r"Ran\s+(\d+)\s+tests?", output)
        if unittest_match:
            results["collected"] = int(unittest_match.group(1))

        # Check unittest failure summary
        if "FAILED (" in output:
            fail_match = re.search(r"failures=(\d+)", output)
            err_match = re.search(r"errors=(\d+)", output)
            if fail_match:
                results["failed"] = int(fail_match.group(1))
            if err_match:
                results["errors"] = int(err_match.group(1))
            results["passed"] = max(0, results["collected"] - results["failed"] - results["errors"])
        elif "OK" in output and results["collected"] > 0:
            results["passed"] = results["collected"]

        # Check pytest output format (e.g., "5 passed, 1 failed in 0.12s")
        pytest_passed = re.search(r"(\d+)\s+passed", output)
        pytest_failed = re.search(r"(\d+)\s+failed", output)
        pytest_errors = re.search(r"(\d+)\s+errors?", output)

        if pytest_passed or pytest_failed:
            passed_cnt = int(pytest_passed.group(1)) if pytest_passed else 0
            failed_cnt = int(pytest_failed.group(1)) if pytest_failed else 0
            error_cnt = int(pytest_errors.group(1)) if pytest_errors else 0
            results["passed"] = passed_cnt
            results["failed"] = failed_cnt
            results["errors"] = error_cnt
            results["collected"] = passed_cnt + failed_cnt + error_cnt

        return results

    def verify_syntax(self, rel_paths: List[str]) -> Dict[str, Any]:
        """Verifies syntax of generated Python files via py_compile."""
        errors = {}
        for rp in rel_paths:
            if not rp.endswith(".py"):
                continue
            safe_p = self.boundary.resolve_safe_path(rp)
            if safe_p.exists() and safe_p.is_file():
                try:
                    py_compile.compile(str(safe_p), doraise=True)
                except py_compile.PyCompileError as e:
                    errors[rp] = str(e)
        return {
            "checked_count": len([p for p in rel_paths if p.endswith(".py")]),
            "syntax_errors": errors,
            "passed": len(errors) == 0
        }

    def verify_completion(
        self,
        reviewer_messages: List[str],
        expected_artifacts: Optional[List[str]] = None,
        test_command: Optional[str] = None,
        verified_hashes: Optional[Dict[str, str]] = None,
        code_to_audit: Optional[str] = None
    ) -> EvidenceValidationResult:
        """
        Evaluates task completion evidence.
        """
        rejection_reasons = []

        # 1. Check Reviewer recommendation
        if reviewer_messages:
            reviewer_recommended = any(
                any(token in msg.upper() for token in ["TASK_COMPLETED", "RECOMMEND_COMPLETION", "APPROVED", "VERIFIED", "COMPLETED"])
                for msg in reviewer_messages
            )
            if not reviewer_recommended:
                rejection_reasons.append("Reviewer has not recommended completion (missing 'TASK_COMPLETED' or 'APPROVED').")
        else:
            reviewer_recommended = True

        # 2. Check Expected Artifacts
        artifacts_verified = []
        missing_artifacts = []
        current_hashes = {}

        if expected_artifacts:
            for art in expected_artifacts:
                try:
                    safe_p = self.boundary.resolve_safe_path(art)
                    if not safe_p.exists() or not safe_p.is_file():
                        missing_artifacts.append(art)
                        rejection_reasons.append(f"Expected artifact '{art}' is missing or not a file.")
                    elif safe_p.stat().st_size == 0:
                        missing_artifacts.append(art)
                        rejection_reasons.append(f"Expected artifact '{art}' exists but is empty (0 bytes).")
                    else:
                        h = self.compute_file_hash(art)
                        current_hashes[art] = h
                        artifacts_verified.append({
                            "rel_path": art,
                            "size_bytes": safe_p.stat().st_size,
                            "sha256": h
                        })
                except Exception as e:
                    missing_artifacts.append(art)
                    rejection_reasons.append(f"Invalid artifact path '{art}': {str(e)}")

        # 3. Check Stale Verification (if previous hashes were provided)
        stale_files = []
        if verified_hashes:
            stale_files = self.check_stale_evidence(verified_hashes)
            if stale_files:
                rejection_reasons.append(
                    f"Stale verification: Files were modified after tests passed: {stale_files}"
                )

        # 4. Check Acceptance Test Suite Execution
        test_results = {}
        if test_command:
            res: StructuredExecutionResult = self.boundary.execute_command(test_command)
            test_results = self.parse_test_output(res.output, res.exit_code)

            if res.exit_code != 0:
                rejection_reasons.append(
                    f"Acceptance test command failed with exit code {res.exit_code}."
                )

            # Prevent zero-test passes!
            if test_results["collected"] == 0:
                rejection_reasons.append(
                    "Zero tests were collected or executed in the acceptance test suite."
                )
            elif test_results["failed"] > 0 or test_results["errors"] > 0:
                rejection_reasons.append(
                    f"Acceptance tests contained failures: {test_results['failed']} failed, {test_results['errors']} errors."
                )

        # 5. Check Python Syntax
        checked_paths = list(current_hashes.keys())
        syntax_res = self.verify_syntax(checked_paths)
        if not syntax_res["passed"]:
            rejection_reasons.append(
                f"Syntax errors detected in generated code: {syntax_res['syntax_errors']}"
            )

        # 6. Advisory Ponytail Bloat Scoring (Non-blocking unless syntax/tests fail)
        bloat_advisory = {}
        if code_to_audit:
            bloat_advisory = audit_code_for_bloat(code_to_audit)

        all_passed = len(rejection_reasons) == 0

        return EvidenceValidationResult(
            passed=all_passed,
            reviewer_recommended=reviewer_recommended,
            artifacts_verified=artifacts_verified,
            missing_artifacts=missing_artifacts,
            test_results=test_results,
            syntax_results=syntax_res,
            verified_hashes=current_hashes,
            stale_files=stale_files,
            bloat_advisory=bloat_advisory,
            rejection_reasons=rejection_reasons
        )
