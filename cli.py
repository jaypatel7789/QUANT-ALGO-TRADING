"""
Direct Interactive Multi-Agent Brain CLI & Terminal
Allows direct prompt submission, real-time agent dialogue streaming,
task history inspection, and Windows PowerShell host execution.
"""
import os
import sys
import time
import asyncio
import threading
from pathlib import Path

# Fix Windows stdout encoding for emojis and ANSI
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")  # Enable VT100 / ANSI escape sequences in Windows console

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.orchestrator import MultiAgentOrchestrator
from core.config import PRIMARY_MODEL, OMNIROUTE_BASE_URL, WORKSPACE_DIR

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[96m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"

AGENT_COLORS = {
    "Architect": CYAN,
    "NemotronSuper": MAGENTA,
    "Reasoner": MAGENTA,
    "Engineer": YELLOW,
    "QuantTrader": GREEN,
    "FullStackDev": BLUE,
    "Reviewer": RED,
    "SystemExecutor": WHITE,
    "System": GRAY,
    "QA": GREEN
}

AGENT_ICONS = {
    "Architect": "📐",
    "NemotronSuper": "🧠",
    "Reasoner": "🧠",
    "Engineer": "⚡",
    "QuantTrader": "📈",
    "FullStackDev": "🌐",
    "Reviewer": "🛡️",
    "SystemExecutor": "🔒",
    "System": "⚙️",
    "QA": "✓"
}

class BrainCLI:
    def __init__(self):
        print(f"{DIM}Initializing Meta-Brain & Multi-Agent Orchestrator...{RESET}")
        self.orchestrator = MultiAgentOrchestrator()
        self.orchestrator.subscribe(self.handle_event)
        self.is_task_running = False

    def handle_event(self, event: dict):
        """Streams real-time agent deliberation to the console."""
        evt_type = event.get("type", "")
        sender = event.get("sender", "Agent")
        content = event.get("content", "")

        color = AGENT_COLORS.get(sender, WHITE)
        icon = AGENT_ICONS.get(sender, "🤖")

        if evt_type == "agent_message" and content:
            print(f"\n{BOLD}{color}{icon} [{sender}]{RESET}")
            print(f"{color}{content.strip()}{RESET}\n")

        elif evt_type == "command_start":
            cmd = content or (event.get("data") or {}).get("command", "")
            print(f"{GRAY}  ▶ PS> {cmd}{RESET}")

        elif evt_type == "command_finish":
            data = event.get("data") or {}
            exit_code = data.get("exit_code", 0)
            duration = data.get("duration", 0)
            output = content or ""
            if exit_code == 0:
                print(f"{GREEN}  ✓ [EXIT 0] ({duration}s){RESET}")
                if output.strip():
                    for line in output.strip().split("\n")[:6]:
                        print(f"{DIM}    {line}{RESET}")
                    if len(output.strip().split("\n")) > 6:
                        print(f"{DIM}    ... [output truncated]{RESET}")
            else:
                print(f"{RED}  ✗ [FAILED exit {exit_code}] ({duration}s){RESET}")
                if output.strip():
                    for line in output.strip().split("\n")[:6]:
                        print(f"{RED}    {line}{RESET}")

        elif evt_type == "task_finished":
            status = (event.get("data") or {}).get("status", "completed")
            dur = event.get("duration") or (event.get("data") or {}).get("duration", 0)
            print(f"\n{BOLD}{GREEN}========================================================================{RESET}")
            print(f"{BOLD}{GREEN}✓ MISSION COMPLETED [{status.upper()}] (Duration: {dur}s){RESET}")
            print(f"{BOLD}{GREEN}========================================================================{RESET}\n")
            self.is_task_running = False

    def print_banner(self):
        print(f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════════╗
║        🧠  AG2 MULTI-AGENT BRAIN TERMINAL (Direct Interactive CLI)       ║
╚══════════════════════════════════════════════════════════════════════════╝{RESET}
 {BOLD}Engine:{RESET} {GREEN}{PRIMARY_MODEL}{RESET} | {BOLD}Gateway:{RESET} {WHITE}{OMNIROUTE_BASE_URL}{RESET} | {BOLD}Workspace:{RESET} {WHITE}{WORKSPACE_DIR}{RESET}
 {BOLD}Agents Active:{RESET} Architect, NemotronSuper, Engineer, QuantTrader, FullStackDev, Reviewer

 {DIM}Direct Commands:
   /help          Show this command menu
   /tasks         List durable tasks & status from SQLite store
   /view <id>     Replay the full dialogue and outputs of a past task
   /cmd <command> Execute a PowerShell command directly in workspace
   /skills        List active skills, quant strategies & agent personas
   /brain         Inspect Meta-Brain cognitive inventory
   /clear         Clear the terminal screen
   /exit          Quit the Brain CLI{RESET}
════════════════════════════════════════════════════════════════════════════
""")

    def cmd_tasks(self):
        """Displays formatted task history."""
        tasks = self.orchestrator.store.list_tasks(limit=15)
        if not tasks:
            print(f"{YELLOW}No durable tasks found in store.{RESET}\n")
            return

        print(f"\n{BOLD}{CYAN}--- RECENT DURABLE TASKS (SQLite Store) ---{RESET}")
        print(f"{'ID':<18} {'STATUS':<12} {'STARTED':<12} {'PROMPT'}")
        print("-" * 75)
        for t in tasks:
            tid = t.get("id", "")
            status = t.get("status", "unknown").upper()
            status_color = GREEN if status == "SUCCEEDED" else (YELLOW if status == "RUNNING" else RED)
            started = time.strftime("%H:%M:%S", time.localtime(t.get("created_at", 0)))
            prompt = t.get("prompt", "").replace("\n", " ")
            if len(prompt) > 42:
                prompt = prompt[:39] + "..."
            print(f"{WHITE}{tid:<18}{RESET} {status_color}{status:<12}{RESET} {DIM}{started:<12}{RESET} {prompt}")
        print("-" * 75 + "\n")

    def cmd_view_task(self, task_id: str):
        """Replays all events and dialogue of a specific task."""
        events = self.orchestrator.store.get_events(task_id=task_id, limit=200)
        if not events:
            print(f"{RED}No events found for task ID: {task_id}{RESET}\n")
            return

        task = self.orchestrator.store.get_task(task_id)
        prompt = task.get("prompt", "") if task else "N/A"
        print(f"\n{BOLD}{CYAN}=== REPLAYING TASK: {task_id} ==={RESET}")
        print(f"{BOLD}Prompt:{RESET} {WHITE}{prompt}{RESET}\n")

        for evt in events:
            sender = evt.get("sender", "Agent")
            content = evt.get("content", "")
            etype = evt.get("type", "")
            color = AGENT_COLORS.get(sender, WHITE)
            icon = AGENT_ICONS.get(sender, "🤖")

            if etype == "agent_message" and content:
                print(f"{BOLD}{color}{icon} [{sender}]:{RESET} {content.strip()}\n")
            elif etype == "command_start":
                print(f"{GRAY}  ▶ PS> {content}{RESET}")
            elif etype == "command_finish":
                print(f"{GREEN}  ✓ {content}{RESET}")
        print(f"{BOLD}{CYAN}=== END OF REPLAY ==={RESET}\n")

    def cmd_powershell(self, command: str):
        """Runs a command via the sandboxed system executor."""
        if not command.strip():
            print(f"{YELLOW}Usage: /cmd <powershell command>{RESET}\n")
            return
        print(f"{DIM}Executing: {command}...{RESET}")
        res = self.orchestrator.team.executor.execute_command(command, shell_type="powershell")
        if res.get("success"):
            print(f"{GREEN}[EXIT 0] ({res.get('duration')}s):{RESET}")
            print(res.get("output") or "[No output]")
        else:
            print(f"{RED}[FAILED exit {res.get('exit_code')}]:{RESET}")
            print(res.get("output") or res.get("stderr") or "[Error]")
        print()

    def cmd_skills(self):
        """Shows summary of indexed skills and personas."""
        skills = self.orchestrator.brain.skill_hub.list_available_skills()
        print(f"\n{BOLD}{CYAN}--- LOADED SKILLS & STRATEGIES ({len(skills)} indexed) ---{RESET}")
        for s in skills[:12]:
            print(f" • {BOLD}{WHITE}{s.get('name')}{RESET} ({s.get('category')}): {DIM}{s.get('description')}{RESET}")
        if len(skills) > 12:
            print(f"{DIM}... and {len(skills) - 12} more skills in repository catalog.{RESET}")
        print()

    def cmd_brain(self):
        """Shows Meta-Brain system inventory."""
        inv = self.orchestrator.brain.get_system_inventory()
        print(f"\n{BOLD}{CYAN}=== META-BRAIN INVENTORY ==={RESET}")
        print(f"{BOLD}Models:{RESET}")
        for m in inv.get("models", []):
            print(f"  • {BOLD}{m.get('id')}{RESET} ({m.get('provider')}): {m.get('role')}")
        print(f"\n{BOLD}Autonomous Repositories:{RESET}")
        for r in inv.get("repositories", []):
            print(f"  • {BOLD}{r.get('name')}{RESET}: {r.get('role')} - {GREEN}{r.get('status')}{RESET}")
        print()

    def dispatch_prompt(self, prompt: str):
        """Dispatches a prompt to the multi-agent team and streams output."""
        task = self.orchestrator.store.create_task(
            prompt=prompt,
            workspace_dir=str(self.orchestrator.workspace)
        )
        task_id = task["id"]
        print(f"\n{BOLD}{CYAN}>>> TASK DISPATCHED: {task_id}{RESET}")
        print(f"{DIM}Activating Agent Team and Meta-Brain reasoning loop...{RESET}\n")

        self.is_task_running = True
        
        # Run synchronously in CLI so user waits and sees streaming
        try:
            self.orchestrator.dispatch_task(task_prompt=prompt, max_turns=20, task_id=task_id)
        except Exception as e:
            print(f"\n{RED}Error during execution: {e}{RESET}\n")
        finally:
            self.is_task_running = False

    def run(self):
        """Main REPL loop."""
        self.print_banner()

        while True:
            try:
                user_input = input(f"{BOLD}{CYAN}Brain >>> {RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{YELLOW}Exiting Brain CLI. Goodbye!{RESET}")
                break

            if not user_input:
                continue

            # Command handling
            if user_input in ["/exit", "/quit", "exit", "quit"]:
                print(f"{YELLOW}Exiting Brain CLI. Goodbye!{RESET}")
                break

            elif user_input in ["/help", "help", "?"]:
                self.print_banner()

            elif user_input in ["/clear", "clear", "cls"]:
                os.system("cls" if sys.platform == "win32" else "clear")
                self.print_banner()

            elif user_input == "/tasks":
                self.cmd_tasks()

            elif user_input.startswith("/view"):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    self.cmd_view_task(parts[1].strip())
                else:
                    print(f"{YELLOW}Usage: /view <task_id>{RESET}\n")

            elif user_input.startswith("/cmd"):
                cmd = user_input[4:].strip()
                self.cmd_powershell(cmd)

            elif user_input == "/skills":
                self.cmd_skills()

            elif user_input == "/brain":
                self.cmd_brain()

            else:
                # Direct task prompt
                self.dispatch_prompt(user_input)

if __name__ == "__main__":
    cli = BrainCLI()
    cli.run()
