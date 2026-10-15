"""
Antigravity Agent Bridge
Connects the Google Antigravity SDK (google-antigravity) and Antigravity IDE models
directly into the AG2 multi-agent project.
"""
import sys
import asyncio
from pathlib import Path
from typing import Optional, AsyncGenerator

BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    ANTIGRAVITY_SDK_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_SDK_AVAILABLE = False

class AntigravityAgentBridge:
    """
    Bridge connecting Google Antigravity models (Gemini 3.8 Flash, Pro, etc.)
    as an autonomous agent inside the multi-agent grid.
    """
    def __init__(self, system_instructions: str = None, model: str = None):
        self.instructions = system_instructions or (
            "You are the Antigravity Meta-Agent, powered by Google Antigravity. "
            "You specialize in deep multimodal reasoning, codebase analysis, and task orchestration."
        )
        self.model = model
        self.is_available = ANTIGRAVITY_SDK_AVAILABLE

    async def execute_prompt(self, prompt: str) -> str:
        """
        Executes a prompt using the Antigravity Agent runtime and returns the text response.
        """
        if not self.is_available:
            return "[Error] google-antigravity SDK is not installed in the active environment."

        try:
            config = LocalAgentConfig(
                system_instructions=self.instructions,
                capabilities=CapabilitiesConfig()
            )
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                full_text = ""
                async for token in response:
                    full_text += token
                return full_text
        except Exception as e:
            return f"[Antigravity Runtime Notice] Agent execution: {e}"

    async def stream_prompt(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Streams response tokens directly from the Antigravity agent.
        """
        if not self.is_available:
            yield "[Error] google-antigravity SDK is not available."
            return

        try:
            config = LocalAgentConfig(
                system_instructions=self.instructions,
                capabilities=CapabilitiesConfig()
            )
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                async for token in response:
                    yield token
        except Exception as e:
            yield f"[Antigravity Error] {e}"

if __name__ == "__main__":
    bridge = AntigravityAgentBridge()
    print("Antigravity SDK Installed & Ready:", bridge.is_available)
