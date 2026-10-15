"""
Core Configuration Module
Connects AG2 agents to the local OmniRoute AI Gateway (http://localhost:20128/v1).
"""
import os
from pathlib import Path
from dotenv import load_dotenv
try:
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelInfo
except ImportError:
    OpenAIChatCompletionClient = None
    class ModelInfo:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

# Load root .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Gateway Settings
OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNIROUTE_API_KEY = (
    os.getenv("EXPLABS_API_KEY")
    or os.getenv("EXPERIENTIAL_API_KEY")
    or os.getenv("OPENROUTER_API_KEY")
    or os.getenv("OMNIROUTE_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or "sk-omniroute-local"
)
OMNIROUTE_HOST = os.getenv("OMNIROUTE_HOST", "127.0.0.1")
OMNIROUTE_PORT = int(os.getenv("OMNIROUTE_PORT", "20128"))

# Model Selection (Routed through OmniRoute)
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "claude-3-7-sonnet")
SECONDARY_MODEL = os.getenv("SECONDARY_MODEL", "gpt-4o")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-2.5-flash")

# Workspace execution path
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", str(BASE_DIR / "workspace")))
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "180"))
HUMAN_INPUT_MODE = os.getenv("HUMAN_INPUT_MODE", "NEVER")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EXPLABS_API_KEY = os.getenv("EXPLABS_API_KEY") or os.getenv("EXPERIENTIAL_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
EXPLABS_BASE_URL = os.getenv("EXPLABS_BASE_URL", "https://api.experientiallabs.ai/v1")

def get_model_client(model_name: str = None, temperature: float = 0.2) -> OpenAIChatCompletionClient:
    """
    Creates an OpenAIChatCompletionClient instance pointing to
    the appropriate endpoint (OpenRouter, Experiential Labs, or OmniRoute).
    """
    model = model_name or PRIMARY_MODEL
    
    # Auto-detect OpenRouter models
    if any(k in model.lower() for k in ["nvidia/", "qwen/", "cohere/", ":free", "meta-llama/"]):
        base_url = OPENROUTER_BASE_URL
        api_key = OPENROUTER_API_KEY or OMNIROUTE_API_KEY
    elif any(k in model.lower() for k in ["grok", "luna", "gpt-5.6"]):
        base_url = EXPLABS_BASE_URL
        api_key = EXPLABS_API_KEY or OMNIROUTE_API_KEY
    else:
        base_url = OMNIROUTE_BASE_URL
        api_key = OMNIROUTE_API_KEY

    # Configure model capabilities so proxying works reliably
    model_info = ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        structured_output=True,
        family="unknown"
    )

    return OpenAIChatCompletionClient(
        model=model,
        base_url=base_url,
        api_key=api_key,
        model_info=model_info,
        include_name_in_message=False,
        temperature=temperature,
        timeout=120
    )

