"""
Multi-Agent Team Definition (Powered by AG2 / AutoGen 0.4+)
Defines Architect, Engineer, Reviewer, and SystemExecutor agents
with integrated Ponytail rules, Graphify knowledge graph, and Windows shell execution.
"""
from typing import Dict, Any, List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

from core.config import get_model_client, WORKSPACE_DIR
from core.executor import WindowsSystemExecutor
from core.skills.ponytail_rules import PONYTAIL_PHILOSOPHY, audit_code_for_bloat
from core.skills.graphify_skill import GraphifySkill
from core.skills.git_skill import GitSkill
from core.skills.system_skill import SystemSkill
from core.skills.rerank_skill import RerankSkill
from core.skills.skill_hub import SkillHub
from core.skills.algo_trading_skill import AlgoTradingSkill
from core.skills.web_production_skill import WebProductionSkill

class AgentTeam:
    def __init__(self, workspace_path: str = None, model_name: str = None):
        self.workspace = str(workspace_path or WORKSPACE_DIR)
        self.executor = WindowsSystemExecutor(self.workspace)
        self.graphify = GraphifySkill(self.workspace)
        self.git = GitSkill(self.workspace)
        self.sys_skill = SystemSkill(self.workspace)
        self.rerank = RerankSkill()
        self.skill_hub = SkillHub()
        self.algo_skill = AlgoTradingSkill()
        self.web_skill = WebProductionSkill()
        self.model_client = get_model_client(model_name)

        self._init_tools()
        self._init_agents()

    def _init_tools(self):
        """Prepares Python functions as callable tools for agents."""
        def index_codebase(target_path: str = "") -> str:
            """Indexes workspace files into an AST knowledge graph."""
            res = self.graphify.index_codebase(target_path if target_path else None)
            return str(res)

        def query_symbol(symbol: str) -> str:
            """Queries the knowledge graph for a function, class, or dependency."""
            res = self.graphify.query_symbol(symbol)
            return str(res)

        def audit_bloat(code: str) -> str:
            """Audits code against Ponytail minimalism rules."""
            res = audit_code_for_bloat(code)
            return str(res)

        def run_powershell(command: str) -> str:
            """Executes a PowerShell command in the workspace and returns output."""
            res = self.executor.execute_command(command, shell_type="powershell")
            return f"Exit Code: {res['exit_code']}\nOutput:\n{res['output']}"

        def read_workspace_file(rel_path: str) -> str:
            """Reads a file in the workspace."""
            return self.sys_skill.read_file(rel_path)

        def write_workspace_file(rel_path: str, content: str) -> str:
            """Writes a file in the workspace."""
            return self.sys_skill.write_file(rel_path, content)

        def rerank_snippets(query: str, snippets_newline_delimited: str) -> str:
            """Semantically reranks a list of code snippets or documents against a query using Nvidia Nemotron Reranker."""
            lines = [s.strip() for s in snippets_newline_delimited.split("---") if s.strip()]
            if not lines:
                lines = [s.strip() for s in snippets_newline_delimited.splitlines() if s.strip()]
            res = self.rerank.rerank_texts(query, lines)
            return str(res)

        def consult_skill(skill_name: str) -> str:
            """Consults the Skill Hub for guidelines on TDD, security hardening, performance, API design, etc."""
            return self.skill_hub.consult_skill(skill_name)

        def calculate_indicators(prices_csv: str) -> str:
            """Calculates SMA-20, EMA-20, and RSI-14 on a comma-separated price string."""
            try:
                nums = [float(x.strip()) for x in prices_csv.split(",") if x.strip()]
                return str(self.algo_skill.calculate_indicators(nums))
            except Exception as e:
                return f"Error calculating indicators: {e}"

        def backtest_ma_strategy(prices_csv: str, fast: int = 5, slow: int = 20) -> str:
            """Executes an event-driven Moving Average Crossover backtest, calculating Sharpe, Drawdown, and Win Rate."""
            try:
                nums = [float(x.strip()) for x in prices_csv.split(",") if x.strip()]
                return str(self.algo_skill.backtest_simple_strategy(nums, fast_period=fast, slow_period=slow))
            except Exception as e:
                return f"Error backtesting: {e}"

        def get_fastapi_template(app_name: str) -> str:
            """Returns production-grade FastAPI microservice template with CORS and health checks."""
            return self.web_skill.get_fastapi_production_template(app_name)

        def get_web_ui_template(title: str) -> str:
            """Returns modern, glassmorphic dark-mode web application HTML template."""
            return self.web_skill.get_production_html_template(title)

        def consult_agency_agent(agent_name: str) -> str:
            """Consults one of the 303 specialized agency agent personas (e.g. investment-researcher, backend-architect)."""
            return self.skill_hub.consult_agency_agent(agent_name)

        def consult_hedge_fund_strategy(strategy_name: str) -> str:
            """Retrieves an AI hedge fund strategy blueprint (deep-value, fundamental-ls, earnings-drift, inflections)."""
            return self.skill_hub.consult_hedge_fund_strategy(strategy_name)

        self.tools = {
            "index_codebase": index_codebase,
            "query_symbol": query_symbol,
            "audit_bloat": audit_bloat,
            "run_powershell": run_powershell,
            "read_workspace_file": read_workspace_file,
            "write_workspace_file": write_workspace_file,
            "rerank_snippets": rerank_snippets,
            "consult_skill": consult_skill,
            "consult_agency_agent": consult_agency_agent,
            "consult_hedge_fund_strategy": consult_hedge_fund_strategy,
            "calculate_indicators": calculate_indicators,
            "backtest_ma_strategy": backtest_ma_strategy,
            "get_fastapi_template": get_fastapi_template,
            "get_web_ui_template": get_web_ui_template
        }

    def _init_agents(self):
        # 1. Architect (Ponytail Rule Enforcer & System Planner)
        self.architect = AssistantAgent(
            name="Architect",
            model_client=self.model_client,
            tools=[self.tools["audit_bloat"], self.tools["consult_skill"], self.tools["consult_agency_agent"]],
            system_message=f"""You are the Lead Architect.
Your role:
- Plan the system architecture concisely.
- Consult the Skill Hub (consult_skill) or Agency Personas (consult_agency_agent) for engineering standards.
- Strictly enforce the Ponytail philosophy:
{PONYTAIL_PHILOSOPHY}
- Prioritize minimalism: reject bloat, avoid premature abstractions, use standard libraries.
- Hand off implementation specs to the Engineer, QuantTrader, or FullStackDev."""
        )

        # 2. Engineer (Graphify-assisted Developer)
        self.engineer = AssistantAgent(
            name="Engineer",
            model_client=self.model_client,
            tools=[
                self.tools["index_codebase"],
                self.tools["query_symbol"],
                self.tools["rerank_snippets"],
                self.tools["consult_skill"],
                self.tools["consult_agency_agent"],
                self.tools["run_powershell"],
                self.tools["read_workspace_file"],
                self.tools["write_workspace_file"]
            ],
            system_message="""You are the Senior Engineer.
Your role:
- Implement clean, minimal, robust code following the Architect's design.
- Query Graphify AST (query_symbol) to inspect existing code before adding logic.
- Use rerank_snippets to semantically find the most relevant code or docs.
- Consult consult_skill or consult_agency_agent for best practice templates when needed.
- Use write_workspace_file to write code and run_powershell to compile or run tests.
- Pass code and test results to the Reviewer for verification."""
        )

        # 3. QuantTrader (Algo-Trading, Backtesting & Risk Specialist)
        self.quant_trader = AssistantAgent(
            name="QuantTrader",
            model_client=self.model_client,
            tools=[
                self.tools["calculate_indicators"],
                self.tools["backtest_ma_strategy"],
                self.tools["consult_hedge_fund_strategy"],
                self.tools["consult_agency_agent"],
                self.tools["write_workspace_file"],
                self.tools["read_workspace_file"],
                self.tools["run_powershell"]
            ],
            system_message="""You are the Quantitative Trader & Backtesting Specialist.
Your role:
- Develop mathematical and algorithmic trading models, risk management systems, and backtests.
- Calculate Sharpe Ratio, Max Drawdown, Win Rate, and position sizing.
- Use backtest_ma_strategy and calculate_indicators to validate strategies against price series.
- Ensure risk guardrails (stop loss, take profit) are mathematically sound.
- Hand off working strategy code and backtest statistics to the Reviewer."""
        )

        # 4. FullStackDev (Production Web & Tool Builder)
        self.fullstack_dev = AssistantAgent(
            name="FullStackDev",
            model_client=self.model_client,
            tools=[
                self.tools["get_fastapi_template"],
                self.tools["get_web_ui_template"],
                self.tools["write_workspace_file"],
                self.tools["read_workspace_file"],
                self.tools["run_powershell"]
            ],
            system_message="""You are the Full-Stack Web & Software Specialist.
Your role:
- Build complete production-grade web applications, REST APIs, and responsive user interfaces.
- Use get_fastapi_template and get_web_ui_template for clean, production-ready boilerplates.
- Ensure modern UI aesthetics (glassmorphism, dark themes, responsive layouts) without placeholders.
- Pass code and verified endpoints to the Reviewer."""
        )

        # 5. Reviewer (QA, Security & Ponytail Bloat Auditor)
        self.reviewer = AssistantAgent(
            name="Reviewer",
            model_client=self.model_client,
            tools=[self.tools["audit_bloat"], self.tools["consult_skill"], self.tools["read_workspace_file"]],
            system_message="""You are the Code Reviewer and QA Specialist.
Your role:
- Review the code for bugs, security vulnerabilities, and logic flaws.
- Run audit_bloat on code to ensure it satisfies Ponytail simplicity.
- Consult consult_skill('security-and-hardening') or other QA skills when reviewing.
- Ensure all tests and backtests pass.
- When all requirements are satisfied and tests pass, reply with 'TASK_COMPLETED'."""
        )

        # 6. System Executor (Local Windows Shell & OS Controller)
        self.system_executor = AssistantAgent(
            name="SystemExecutor",
            model_client=self.model_client,
            tools=[
                self.tools["run_powershell"],
                self.tools["read_workspace_file"],
                self.tools["write_workspace_file"]
            ],
            system_message="""You are the System Executor.
You have full control over the local Windows host environment via PowerShell.
Execute test commands, build scripts, and git operations requested by the team."""
        )

        # 7. NemotronSuper (120B Super Reasoning & Logic Specialist)
        self.nemotron_client = get_model_client("nvidia/nemotron-3-super-120b-a12b:free")
        self.nemotron_super = AssistantAgent(
            name="NemotronSuper",
            model_client=self.nemotron_client,
            tools=[
                self.tools["consult_skill"],
                self.tools["audit_bloat"],
                self.tools["query_symbol"],
                self.tools["rerank_snippets"]
            ],
            system_message="""You are the Nemotron Super Reasoning Specialist, powered by NVIDIA Nemotron-3 Super 120B.
Your role:
- Deep reasoning, mathematical proof, algorithm design, and complex problem decomposition.
- Provide step-by-step reasoning tokens and rigorous logic for challenging tasks.
- Assist the Architect and Engineer with algorithmic complexity, edge cases, and high-concurrency design.
- Hand off conclusions to the Engineer, QuantTrader, or FullStackDev."""
        )

    def create_targeted_team(self, task_type: str = "general", max_turns: int = 20):
        """
        Activates only the minimal, targeted sub-team needed for the task,
        drastically reducing latency, LLM rounds, and token costs:
        - Quant / Trading: QuantTrader + Reviewer (2 agents)
        - UI/Web task: FullStackDev + Reviewer (2 agents)
        - Difficult algorithm / math: Engineer + NemotronSuper + Reviewer (3 agents)
        - Architecture task: Architect + Engineer + Reviewer (3 agents)
        - Small bug: Engineer + Reviewer (2 agents)
        """
        tt = task_type.lower()
        if any(w in tt for w in ["quant", "trade", "trading", "backtest", "finance", "stock", "hedge", "rsi", "macd", "indicator"]):
            participants = [self.quant_trader, self.reviewer]
        elif any(w in tt for w in ["ui", "web", "html", "css", "frontend", "fullstack", "dashboard"]):
            participants = [self.fullstack_dev, self.reviewer]
        elif any(w in tt for w in ["algo", "algorithm", "math", "proof", "reason", "puzzle", "logic"]):
            participants = [self.engineer, self.nemotron_super, self.reviewer]
        elif any(w in tt for w in ["arch", "architecture", "design", "plan", "system", "blueprint"]):
            participants = [self.architect, self.engineer, self.reviewer]
        elif any(w in tt for w in ["bug", "debug", "fix", "investigate", "error", "unit test", "regression"]):
            participants = [self.engineer, self.reviewer]
        else:
            participants = [self.architect, self.engineer, self.reviewer]

        termination = TextMentionTermination("TASK_COMPLETED") | MaxMessageTermination(max_turns)
        return SelectorGroupChat(
            participants=participants,
            model_client=self.model_client,
            termination_condition=termination,
            max_turns=max_turns
        )

    def create_team(self, max_turns: int = 25):
        """
        Creates a collaborative group chat team with only cognitive agents.
        SystemExecutor is maintained as an execution service, not a conversational participant.
        """
        termination = TextMentionTermination("TASK_COMPLETED") | MaxMessageTermination(max_turns)
        participants = [
            self.architect,
            self.engineer,
            self.nemotron_super,
            self.quant_trader,
            self.fullstack_dev,
            self.reviewer
        ]

        team = SelectorGroupChat(
            participants=participants,
            model_client=self.model_client,
            termination_condition=termination,
            max_turns=max_turns
        )
        return team
