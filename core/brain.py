"""
The Meta-Brain Controller
Coordinates multi-agent tasks, selects optimal LLM models and capabilities,
injects skills from the 6 cloned repositories, and verifies execution outputs.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.skills.skill_hub import SkillHub
from core.skills.ponytail_rules import audit_code_for_bloat
from core.skills.graphify_skill import GraphifySkill
from core.skills.rerank_skill import RerankSkill
from core.config import (
    PRIMARY_MODEL,
    SECONDARY_MODEL,
    FALLBACK_MODEL,
    WORKSPACE_DIR
)

class MetaBrain:
    """
    Central cognitive coordinator.
    Evaluates mission directives, allocates optimal models, skills, and repositories,
    and conducts automated quality assurance.
    """
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or WORKSPACE_DIR)
        self.skill_hub = SkillHub()
        self.graphify = GraphifySkill(str(self.workspace))
        self.reranker = RerankSkill()
        self.repo_dir = BASE_DIR / "repos"

    def get_system_inventory(self) -> Dict[str, Any]:
        """Returns the full catalog of models, agents, skills, and cloned repositories."""
        models = [
            {"id": "grok-4.7", "provider": "Experiential Labs", "tier": "Fast Logic & High Concurrency", "role": "Primary Engineer"},
            {"id": "gpt-5.6-luna", "provider": "Experiential Labs", "tier": "Long Context & Low Cost", "role": "Researcher & Secondary Engineer"},
            {"id": "nvidia/nemotron-3-ultra-550b-a55b:free", "provider": "OpenRouter", "tier": "550B Flagship Reasoning", "role": "Lead Architect & Deep QA"},
            {"id": "nvidia/nemotron-3-super-120b-a12b:free", "provider": "OpenRouter", "tier": "120B Super Reasoning & Fast Streamer", "role": "Architect & Deep Logic Specialist"},
            {"id": "cohere/north-mini-code:free", "provider": "OpenRouter", "tier": "Code Synthesis", "role": "Code Generation Fallback"},
            {"id": "nvidia/llama-nemotron-rerank-vl-1b-v2:free", "provider": "OpenRouter", "tier": "Document & Code Reranker", "role": "Semantic Search Skill"}
        ]

        repos = [
            {"name": "ai-hedge-fund", "role": "Multi-Agent Hedge Fund Strategies & Risk Limits", "status": f"Ready ({len(self.skill_hub.hedge_fund_strategies)} strategies)"},
            {"name": "agency-agents", "role": "303 Enterprise Agent Personas Across 12 Divisions", "status": f"Loaded ({len(self.skill_hub.agency_agents_cache)} personas)"},
            {"name": "OpenBB", "role": "Financial Market Data & Institutional Analysis Platform", "status": "Ready"},
            {"name": "qlib", "role": "Microsoft AI-Oriented Quantitative Investment Platform", "status": "Ready"},
            {"name": "FinRL", "role": "Deep Reinforcement Learning Financial Trading (PPO/DQN)", "status": "Ready"},
            {"name": "CloddsBot", "role": "Sports & Market Odds Arbitrage Trading Engine", "status": "Ready"},
            {"name": "Graft", "role": "AI Code Grafting & Automated AST Migration", "status": "Ready"},
            {"name": "OpenMontage", "role": "Multimodal Creative & Video Production Pipelines", "status": "Ready"},
            {"name": "codebase-memory-mcp", "role": "Codebase Semantic Memory MCP Server", "status": "Ready"},
            {"name": "serena", "role": "Language Server Protocol (LSP) Code Navigation", "status": "Ready"},
            {"name": "ponytail", "role": "Senior Developer Minimalism & Anti-Bloat Rules", "status": "Ready"},
            {"name": "OmniRoute", "role": "Local Multi-Provider AI Gateway (:20128)", "status": "Active"},
            {"name": "graphify", "role": "AST Knowledge Graph Indexing & Symbol Map", "status": "Ready"},
            {"name": "agent-skills", "role": "25 Production Engineering Skills (Addy Osmani)", "status": f"Loaded ({len(self.skill_hub.skills_cache)} skills)"},
            {"name": "freellmapi", "role": "Free LLM Endpoint Proxy & Catalog", "status": "Ready"},
            {"name": "backtesting.py", "role": "Ultra-Fast Python Strategy Backtesting Engine", "status": "Ready"},
            {"name": "ccxt", "role": "Universal Exchange API (Crypto & Multi-Asset)", "status": "Ready"},
            {"name": "fastapi-best-practices", "role": "Enterprise Production API Blueprint", "status": "Ready"},
            {"name": "OpenTerminal", "role": "Extensible Agent Terminal & Command Interface", "status": "Ready"},
            {"name": "openclaw", "role": "Autonomous Web Scraping & Browser Automation", "status": "Ready"},
            {"name": "superpowers", "role": "Systematic Debugging, Worktrees & Planning Skills", "status": f"Ready (15 skills)"},
            {"name": "hermes-agent", "role": "NousResearch Tool Calling, Reasoning & Mini-SWE Loop", "status": "Ready"},
            {"name": "ECC", "role": "Enhanced Code Controller & Multi-Agent Workflows", "status": f"Loaded (292 skills)"},
            {"name": "opencode", "role": "Autonomous AI Software Engineer Engine", "status": "Ready"}
        ]

        agents = [
            {"name": "Architect", "role": "Lead System Planner", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "specialty": "Ponytail Minimalism & High-Level Architecture"},
            {"name": "NemotronSuper", "role": "120B Super Reasoning Specialist", "model": "nvidia/nemotron-3-super-120b-a12b:free", "specialty": "Deep Logic, Complex Math/Algorithm Reasoning & Streaming Tokens"},
            {"name": "Engineer", "role": "Senior Developer", "model": PRIMARY_MODEL, "specialty": "Modular Code Synthesis & Graphify AST"},
            {"name": "QuantTrader", "role": "Algorithmic Trader & Backtester", "model": "grok-4.7", "specialty": "AI Hedge Fund, Qlib, FinRL, CCXT & Sharpe Backtesting"},
            {"name": "FullStackDev", "role": "Production Web & Tool Specialist", "model": "gpt-5.6-luna", "specialty": "FastAPI, Glassmorphic UI, OpenMontage Media Pipelines"},
            {"name": "Reviewer", "role": "QA & Security Auditor", "model": "grok-4.7", "specialty": "Ponytail Bloat Audit, Security Scans, Test Sign-off"},
            {"name": "SystemExecutor", "role": "Windows OS & Terminal Controller", "model": "Local Host", "specialty": "PowerShell, Git, Pip, Docker"}
        ]

        total_skills_count = len(self.skill_hub.skills_cache) + len(self.skill_hub.agency_agents_cache) + len(self.skill_hub.hedge_fund_strategies)

        return {
            "active_primary_model": PRIMARY_MODEL,
            "models": models,
            "repositories": repos,
            "agents": agents,
            "total_skills": total_skills_count,
            "sample_skills": [s["name"] for s in self.skill_hub.list_available_skills()[:8]] + ["algo_trading_skill", "web_production_skill"]
        }

    def analyze_and_plan(self, task_prompt: str) -> Dict[str, Any]:
        """
        Cognitive strategy planner.
        Classifies incoming tasks and determines optimal agent, model, and skill allocations.
        """
        lower = task_prompt.lower()
        
        # 1. Classify task domain across 24 integrated repositories and skills
        if any(w in lower for w in ["scrape", "crawling", "crawl", "browser automation", "openclaw", "extract web"]):
            domain = "browser_automation_scraping"
            recommended_skill = "frontend-ui-engineering"
            assigned_model = "gpt-5.6-luna"
            primary_agent = "FullStackDev"
        elif any(w in lower for w in ["debug", "root cause", "systematic-debugging", "investigate failure", "trace bug"]):
            domain = "systematic_debugging"
            recommended_skill = "systematic-debugging"
            assigned_model = "grok-4.7"
            primary_agent = "Engineer"
        elif any(w in lower for w in ["swe", "hermes", "opencode", "autonomous coding", "ecc"]):
            domain = "autonomous_software_engineering"
            recommended_skill = "subagent-driven-development"
            assigned_model = PRIMARY_MODEL
            primary_agent = "Engineer"
        elif any(w in lower for w in ["terminal", "openterminal", "shell script", "superpowers"]):
            domain = "terminal_execution_superpowers"
            recommended_skill = "using-superpowers"
            assigned_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
            primary_agent = "SystemExecutor"
        elif any(w in lower for w in ["hedge fund", "buffett", "graham", "cathie", "openbb", "fundamental-ls", "deep-value", "valuation", "portfolio"]):
            domain = "institutional_hedge_fund"
            recommended_skill = "finance-investment-researcher"
            assigned_model = "grok-4.7"
            primary_agent = "QuantTrader"
        elif any(w in lower for w in ["finrl", "qlib", "reinforcement learning", "drl", "ppo", "dqn", "gym"]):
            domain = "reinforcement_learning_trading"
            recommended_skill = "algo_trading_skill"
            assigned_model = "grok-4.7"
            primary_agent = "QuantTrader"
        elif any(w in lower for w in ["arbitrage", "odds", "clodds", "betting", "market maker"]):
            domain = "odds_arbitrage_trading"
            recommended_skill = "algo_trading_skill"
            assigned_model = "grok-4.7"
            primary_agent = "QuantTrader"
        elif any(w in lower for w in ["graft", "ast transform", "code graft", "migrate legacy"]):
            domain = "code_grafting_refactor"
            recommended_skill = "code-simplification"
            assigned_model = PRIMARY_MODEL
            primary_agent = "Engineer"
        elif any(w in lower for w in ["openmontage", "video", "montage", "media render", "creative"]):
            domain = "multimodal_creative_production"
            recommended_skill = "frontend-ui-engineering"
            assigned_model = "gpt-5.6-luna"
            primary_agent = "FullStackDev"
        elif any(w in lower for w in ["mcp", "codebase memory", "memory server", "context graph"]):
            domain = "codebase_memory_mcp"
            recommended_skill = "api-and-interface-design"
            assigned_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
            primary_agent = "Architect"
        elif any(w in lower for w in ["reason", "reasoning", "strawberry", "math", "puzzle", "proof", "complex logic"]):
            domain = "deep_reasoning_logic"
            recommended_skill = "planning-and-task-breakdown"
            assigned_model = "nvidia/nemotron-3-super-120b-a12b:free"
            primary_agent = "NemotronSuper"
        elif any(w in lower for w in ["web app", "website", "frontend", "fullstack", "dashboard", "ui", "html", "css", "vue", "react"]):
            domain = "fullstack_web_production"
            recommended_skill = "frontend-ui-engineering"
            assigned_model = "gpt-5.6-luna"
            primary_agent = "FullStackDev"
        elif any(w in lower for w in ["trade", "trading", "algo", "backtest", "stock", "crypto", "btc", "eth", "rsi", "macd", "indicator", "sharpe", "forex"]):
            domain = "algo_trading_backtest"
            recommended_skill = "algo_trading_skill"
            assigned_model = "grok-4.7"
            primary_agent = "QuantTrader"
        elif any(w in lower for w in ["test", "tdd", "unit test", "pytest"]):
            domain = "test_driven_development"
            recommended_skill = "test-driven-development"
            assigned_model = PRIMARY_MODEL
            primary_agent = "Engineer"
        elif any(w in lower for w in ["security", "auth", "token", "sanitize", "vulnerability"]):
            domain = "security_hardening"
            recommended_skill = "security-and-hardening"
            assigned_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
            primary_agent = "Engineer"
        elif any(w in lower for w in ["refactor", "clean", "bloat", "simplify", "minimal"]):
            domain = "code_simplification"
            recommended_skill = "code-simplification"
            assigned_model = "grok-4.7"
            primary_agent = "Engineer"
        elif any(w in lower for w in ["api", "endpoint", "rest", "fastapi", "route"]):
            domain = "api_design"
            recommended_skill = "api-and-interface-design"
            assigned_model = PRIMARY_MODEL
            primary_agent = "Engineer"
        elif any(w in lower for w in ["perf", "speed", "memory", "optimize", "slow"]):
            domain = "performance_optimization"
            recommended_skill = "performance-optimization"
            assigned_model = "grok-4.7"
            primary_agent = "Engineer"
        else:
            domain = "general_engineering"
            recommended_skill = "planning-and-task-breakdown"
            assigned_model = PRIMARY_MODEL
            primary_agent = "Engineer"

        # Check if user specifically requested an agency agent persona
        for agent_key in self.skill_hub.agency_agents_cache:
            short_name = agent_key.split("-", 1)[-1] if "-" in agent_key else agent_key
            if agent_key in lower or short_name in lower:
                domain = "agency_enterprise_role"
                recommended_skill = agent_key
                break

        # Retrieve relevant guidance from skill hub
        skill_guidance = self.skill_hub.consult_skill(recommended_skill, max_chars=1000)

        allocation_plan = {
            "task": task_prompt,
            "classified_domain": domain,
            "allocated_primary_model": assigned_model,
            "primary_lead_agent": primary_agent,
            "recommended_skill": recommended_skill,
            "skill_snippet": skill_guidance[:300] + "...",
            "agent_team_strategy": [
                {"agent": "Architect", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "directive": f"Enforce Ponytail minimalism + {recommended_skill} architectural standards."},
                {"agent": primary_agent, "model": assigned_model, "directive": f"Lead development in {domain} using dedicated toolsets and repos."},
                {"agent": "SystemExecutor", "model": "Local Host", "directive": "Execute build scripts, test suites, and backtests in Windows PowerShell."},
                {"agent": "Reviewer", "model": "grok-4.7", "directive": "Run Ponytail bloat audit, security verification, and confirm exit code 0."}
            ]
        }

        return allocation_plan

    def verify_work(self, code_content: str, execution_output: str = "") -> Dict[str, Any]:
        """
        Quality assurance gate.
        Audits code against Ponytail minimalism rules and test results.
        """
        bloat_audit = audit_code_for_bloat(code_content)
        passed_tests = "error" not in execution_output.lower() and "fail" not in execution_output.lower()
        is_approved = bloat_audit["score"] >= 80 and passed_tests

        return {
            "approved": is_approved,
            "bloat_score": bloat_audit["score"],
            "recommendation": bloat_audit["recommendation"],
            "findings": bloat_audit["findings"],
            "test_status": "Passed" if passed_tests else "Failed/Warnings Detected"
        }
