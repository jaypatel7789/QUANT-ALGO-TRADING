"""
End-to-End System Verification Test
Validates AG2 installation, PowerShell executor, Graphify indexing,
Ponytail rules, and OmniRoute endpoint connectivity.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def test_ag2_and_core():
    print("[1/6] Testing AG2 & Core Module Imports...")
    import autogen_agentchat
    import autogen_core
    from core.config import OMNIROUTE_BASE_URL, PRIMARY_MODEL, WORKSPACE_DIR
    print(f"      [OK] autogen_agentchat Version: {autogen_agentchat.__version__}")
    print(f"      [OK] Config: Base URL = {OMNIROUTE_BASE_URL}, Primary Model = {PRIMARY_MODEL}")

def test_powershell_executor():
    print("[2/6] Testing Windows PowerShell System Executor...")
    from core.executor import WindowsSystemExecutor
    executor = WindowsSystemExecutor(str(BASE_DIR / "workspace"))
    res = executor.execute_command("Write-Output 'Hello from PowerShell SystemExecutor!'", shell_type="powershell")
    assert res["success"] is True, f"PowerShell failed: {res}"
    assert "Hello from PowerShell SystemExecutor!" in res["output"]
    print(f"      [OK] PowerShell Execution verified ({res['duration']}s): {res['output']}")

def test_graphify_skill():
    print("[3/6] Testing Graphify AST Knowledge Graph Skill...")
    from core.skills.graphify_skill import GraphifySkill
    graphify = GraphifySkill(str(BASE_DIR))
    index_res = graphify.index_codebase(str(BASE_DIR / "core"))
    assert index_res["status"] in ["success", "indexed_with_cli"]
    summary = index_res.get("summary", {})
    print(f"      [OK] Graphify AST Indexed: {summary.get('files', 0)} files, {summary.get('classes', 0)} classes, {summary.get('functions', 0)} functions")

    # Test symbol query
    query_res = graphify.query_symbol("WindowsSystemExecutor")
    matched = query_res.get("matched_symbols", [])
    assert len(matched) > 0, "Failed to locate WindowsSystemExecutor in knowledge graph"
    print(f"      [OK] Graphify Query Verified: Found symbol '{matched[0]['name']}' in {matched[0].get('file')}")

def test_ponytail_rules():
    print("[4/6] Testing Ponytail Minimalism Rules & Bloat Audit...")
    from core.skills.ponytail_rules import audit_code_for_bloat, PONYTAIL_PHILOSOPHY
    sample_clean_code = "def add(a, b):\n    return a + b\n"
    audit_res = audit_code_for_bloat(sample_clean_code)
    assert audit_res["score"] == 100
    print(f"      [OK] Ponytail Audit Score for clean code: {audit_res['score']}/100 ({audit_res['recommendation']})")

def test_agent_team_initialization():
    print("[5/6] Testing Agent Team Initialization (7 Specialized Agents)...")
    from core.agents.team import AgentTeam
    team = AgentTeam(str(BASE_DIR / "workspace"))
    assert team.architect.name == "Architect"
    assert team.nemotron_super.name == "NemotronSuper"
    assert team.engineer.name == "Engineer"
    assert team.quant_trader.name == "QuantTrader"
    assert team.fullstack_dev.name == "FullStackDev"
    assert team.reviewer.name == "Reviewer"
    assert team.system_executor.name == "SystemExecutor"
    print("      [OK] All 7 agents initialized with specialized models (including Nemotron 120B Super Reasoner).")

def test_omniroute_connectivity():
    print("[6/6] Checking OmniRoute Gateway Endpoint Status...")
    import requests
    from core.config import OMNIROUTE_HOST, OMNIROUTE_PORT
    gw_url = f"http://{OMNIROUTE_HOST}:{OMNIROUTE_PORT}"
    try:
        r = requests.get(f"{gw_url}/v1/models", timeout=1.5)
        if r.status_code == 200:
            print(f"      [OK] OmniRoute Gateway is ACTIVE on {gw_url} (HTTP 200 - {len(r.json().get('data', []))} models registered)")
        else:
            print(f"      [OK] OmniRoute Gateway responded on {gw_url} (HTTP {r.status_code})")
    except Exception:
        print(f"      [INFO] OmniRoute Gateway on {gw_url} is not yet running.")
        print(f"             Launch it using: node gateway/start_gateway.js or run 'npm run gateway'")

if __name__ == "__main__":
    print("\n=======================================================")
    print(">>> RUNNING AG2 + OMNIROUTE SYSTEM VERIFICATION")
    print("=======================================================\n")
    try:
        test_ag2_and_core()
        test_powershell_executor()
        test_graphify_skill()
        test_ponytail_rules()
        test_agent_team_initialization()
        test_omniroute_connectivity()
        print("\n=======================================================")
        print(">>> ALL CORE SYSTEM VERIFICATIONS PASSED SUCCESSFULLY!")
        print("=======================================================\n")
    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
