"""
Ponytail Skill - Minimalist Software Engineering & Bloat Prevention
Enforces senior developer simplicity: "The best code is the code you never wrote."
"""
from typing import Dict, Any, List

PONYTAIL_PHILOSOPHY = """
=== PONYTAIL DECISION LADDER ===
Before writing or approving any code, climb this ladder:
1. DOES THIS NEED TO EXIST? (YAGNI - You Aren't Gonna Need It). Reject unnecessary features.
2. IS IT ALREADY IN THE CODEBASE? Check existing utilities and reuse them.
3. DOES THE STANDARD LIBRARY DO IT? Use built-in modules (pathlib, json, urllib, os, sys) before adding third-party packages.
4. IS THERE A NATIVE PLATFORM FEATURE? Use native OS or runtime capabilities.
5. CAN IT BE ONE LINE? Do not write a 50-line class when a clean 3-line function solves the problem.
6. MINIMUM VIABLE SOLUTION: Write the cleanest, most concise code possible without sacrificing security or error handling.
"""

def audit_code_for_bloat(code_text: str) -> Dict[str, Any]:
    """
    Audits a piece of code or file content for architectural bloat,
    over-engineering, and unnecessary complexity.
    """
    lines = [l for l in code_text.splitlines() if l.strip() and not l.strip().startswith("#")]
    num_lines = len(lines)
    findings: List[str] = []
    score = 100

    # Checks
    if num_lines > 300:
        findings.append(f"File is {num_lines} lines long. Consider splitting or eliminating redundant wrappers.")
        score -= 20
    
    overkill_patterns = [
        ("BaseAbstractFactoryManager", "Excessive design pattern abstraction detected."),
        ("BaseHelperUtilitySingleton", "Unnecessary boilerplate class wrapper."),
        ("try:\n    pass\nexcept:", "Swallowed exceptions without logging."),
    ]

    for pattern, warning in overkill_patterns:
        if pattern.lower() in code_text.lower():
            findings.append(warning)
            score -= 15

    recommendation = "Approved: Clean and concise" if score >= 80 else "Needs Simplification: Review against Ponytail Ladder"

    return {
        "score": max(0, score),
        "total_active_lines": num_lines,
        "findings": findings,
        "recommendation": recommendation,
        "ladder_applied": True
    }
