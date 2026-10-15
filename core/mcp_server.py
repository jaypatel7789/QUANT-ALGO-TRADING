"""
Antigravity MCP Server
Exposes the Multi-Agent Platform (7 Agents, 24 Repos, 638 Skills)
directly to the Antigravity IDE and its internal models (Gemini 3.8, Claude, etc.)
via the Model Context Protocol (MCP).
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from mcp.server.fastmcp import FastMCP
from core.brain import MetaBrain
from core.skills.algo_trading_skill import AlgoTradingSkill
from core.skills.ponytail_rules import audit_code_for_bloat
from core.skills.graphify_skill import GraphifySkill
from core.config import WORKSPACE_DIR

mcp = FastMCP(
    "antigravity-multi-agent-grid",
    instructions="Bridge connecting Google Antigravity models to the multi-agent engineering platform."
)

brain = MetaBrain(str(WORKSPACE_DIR))
algo_skill = AlgoTradingSkill()
graphify = GraphifySkill(str(WORKSPACE_DIR))

@mcp.tool(name="get_multi_agent_inventory", description="Get the complete inventory of all 7 agents, 24 repositories, and 638 skills in the project.")
def get_multi_agent_inventory() -> str:
    inv = brain.get_system_inventory()
    lines = [
        f"Active Primary Model: {inv['active_primary_model']}",
        f"Total Skills & Personas: {inv['total_skills']}",
        f"Agents ({len(inv['agents'])}): " + ", ".join([a['name'] for a in inv['agents']]),
        f"Repositories ({len(inv['repositories'])}): " + ", ".join([r['name'] for r in inv['repositories']])
    ]
    return "\n".join(lines)

@mcp.tool(name="plan_and_allot_task", description="Uses the Meta-Brain to analyze a directive, allocate the optimal agents, models, and injected skills.")
def plan_and_allot_task(task_prompt: str) -> str:
    plan = brain.analyze_and_plan(task_prompt)
    lines = [
        f"Classified Domain: {plan['classified_domain']}",
        f"Lead Agent: {plan['primary_lead_agent']} ({plan['allocated_primary_model']})",
        f"Injected Skill / Persona: {plan['recommended_skill']}",
        "Agent Team Strategy:"
    ]
    for s in plan.get("agent_team_strategy", []):
        lines.append(f"  - [{s['agent']} - {s['model']}]: {s['directive']}")
    return "\n".join(lines)

@mcp.tool(name="execute_quant_backtest", description="Run an algorithmic backtest on historical price series and calculate Sharpe Ratio, Max Drawdown, and Win Rate.")
def execute_quant_backtest(prices_csv: str, fast_period: int = 5, slow_period: int = 20) -> str:
    try:
        prices = [float(x.strip()) for x in prices_csv.split(",") if x.strip()]
        result = algo_skill.backtest_simple_strategy(prices, fast_period=fast_period, slow_period=slow_period)
        return str(result)
    except Exception as e:
        return f"Error executing quant backtest: {e}"

@mcp.tool(name="execute_institutional_orderflow_backtest", description="Run an institutional microstructure convergence backtest (Order Flow absorption, Volume Profile Value Area, Options GEX) with FIFO queue position modeling and slippage.")
def execute_institutional_orderflow_backtest(instrument: str = "/ES", initial_capital: float = 50000.0) -> str:
    try:
        result = algo_skill.run_institutional_microstructure_simulation(instrument=instrument, initial_capital=initial_capital)
        lines = [
            f"=== INSTITUTIONAL S&P 500 MICROSTRUCTURE BACKTEST ({instrument}) ===",
            f"Regime: {result['regime']}",
            f"Win Rate: {result['win_rate_pct']}%",
            f"Profit Factor: {result['profit_factor']}",
            f"Net PnL: ${result['net_pnl']:,.2f}",
            f"Total Commission: ${result['total_commission']:,.2f}",
            f"Total Slippage: ${result['total_slippage']:,.2f}",
            f"Sharpe Ratio: {result['sharpe_ratio']}",
            f"Max Drawdown: ${result['max_drawdown_dollars']:,.2f}",
            f"Status: {result['status']}"
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error executing institutional backtest: {e}"

@mcp.tool(name="audit_code_minimalism", description="Audits code against Ponytail senior developer minimalism rules and returns a bloat score.")
def audit_code_minimalism(code: str) -> str:
    result = audit_code_for_bloat(code)
    return f"Bloat Score: {result['score']}/100\nRecommendation: {result['recommendation']}\nFindings: {result['findings']}"

@mcp.tool(name="query_codebase_ast", description="Queries the workspace Graphify AST knowledge graph for classes, functions, or dependencies.")
def query_codebase_ast(symbol_name: str) -> str:
    return str(graphify.query_symbol(symbol_name))

if __name__ == "__main__":
    mcp.run()
