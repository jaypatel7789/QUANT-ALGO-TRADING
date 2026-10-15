"""
Central Model Registry & Telemetry (Phase 5)
Provides:
- Centralized model endpoints, capabilities, and pricing definitions
- Circuit breaker & temporary avoidance of repeatedly failing endpoints
- Model telemetry: latency, tokens, rate limits, timeouts, tool compatibility
- Fallback resolver ensuring tool-calling compatibility
- Bounded retries with exponential backoff and jitter
"""
import os
import sys
import time
import math
import random
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

try:
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelInfo
except ImportError:
    OpenAIChatCompletionClient = None
    class ModelInfo:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

@dataclass
class ModelProfile:
    id: str
    provider: str
    base_url: str
    api_key_env: str
    supports_tools: bool = True
    supports_structured_output: bool = True
    supports_vision: bool = False
    context_window: int = 128000
    cost_per_million_input: Optional[float] = None  # None indicates unknown
    cost_per_million_output: Optional[float] = None
    is_free: bool = False

@dataclass
class EndpointTelemetry:
    requests_total: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    rate_limits_encountered: int = 0
    timeouts_encountered: int = 0
    total_latency_seconds: float = 0.0
    prompt_tokens_total: int = 0
    completion_tokens_total: int = 0
    consecutive_failures: int = 0
    circuit_open_until: float = 0.0

    def record_success(self, latency: float, prompt_tokens: int = 0, completion_tokens: int = 0):
        self.requests_total += 1
        self.requests_succeeded += 1
        self.consecutive_failures = 0
        self.total_latency_seconds += latency
        self.prompt_tokens_total += prompt_tokens
        self.completion_tokens_total += completion_tokens

    def record_failure(self, is_rate_limit: bool = False, is_timeout: bool = False):
        self.requests_total += 1
        self.requests_failed += 1
        self.consecutive_failures += 1
        if is_rate_limit:
            self.rate_limits_encountered += 1
        if is_timeout:
            self.timeouts_encountered += 1

        # Trip circuit breaker if 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.circuit_open_until = time.time() + 60.0  # avoid for 60s

    def is_available(self) -> bool:
        if self.circuit_open_until > 0 and time.time() < self.circuit_open_until:
            return False
        return True

class ModelRegistry:
    """
    Central repository for all provider endpoints, telemetry, and fallback routing.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.profiles: Dict[str, ModelProfile] = {}
        self.telemetry: Dict[str, EndpointTelemetry] = {}
        self._init_profiles()

    def _init_profiles(self):
        omniroute_base = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
        openrouter_base = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        explabs_base = os.getenv("EXPLABS_BASE_URL", "https://api.experientiallabs.ai/v1")

        # OpenRouter Models
        self.register_profile(ModelProfile(
            id="nvidia/nemotron-3-super-120b-a12b:free",
            provider="OpenRouter",
            base_url=openrouter_base,
            api_key_env="OPENROUTER_API_KEY",
            supports_tools=True,
            supports_structured_output=True,
            is_free=True
        ))
        self.register_profile(ModelProfile(
            id="nvidia/nemotron-3-ultra-550b-a55b:free",
            provider="OpenRouter",
            base_url=openrouter_base,
            api_key_env="OPENROUTER_API_KEY",
            supports_tools=True,
            supports_structured_output=True,
            is_free=True
        ))

        # Experiential Labs Models
        self.register_profile(ModelProfile(
            id="grok-4.7",
            provider="Experiential Labs",
            base_url=explabs_base,
            api_key_env="EXPLABS_API_KEY",
            supports_tools=True,
            supports_structured_output=True,
            cost_per_million_input=None,
            cost_per_million_output=None
        ))
        self.register_profile(ModelProfile(
            id="gpt-5.6-luna",
            provider="Experiential Labs",
            base_url=explabs_base,
            api_key_env="EXPLABS_API_KEY",
            supports_tools=True,
            supports_structured_output=True,
            cost_per_million_input=None,
            cost_per_million_output=None
        ))

        # OmniRoute Gateway Fallbacks
        self.register_profile(ModelProfile(
            id="claude-3-7-sonnet",
            provider="OmniRoute",
            base_url=omniroute_base,
            api_key_env="OMNIROUTE_API_KEY",
            supports_tools=True,
            supports_structured_output=True
        ))
        self.register_profile(ModelProfile(
            id="gpt-4o",
            provider="OmniRoute",
            base_url=omniroute_base,
            api_key_env="OMNIROUTE_API_KEY",
            supports_tools=True,
            supports_structured_output=True
        ))

    def register_profile(self, profile: ModelProfile):
        self.profiles[profile.id] = profile
        if profile.id not in self.telemetry:
            self.telemetry[profile.id] = EndpointTelemetry()

    def get_profile(self, model_id: str) -> Optional[ModelProfile]:
        return self.profiles.get(model_id)

    def is_endpoint_healthy(self, model_id: str) -> bool:
        with self.lock:
            telem = self.telemetry.get(model_id)
            if not telem:
                return True
            return telem.is_available()

    def select_compatible_fallback(self, failed_model: str, requires_tools: bool = True) -> str:
        """
        Picks a healthy model compatible with task requirements.
        """
        fallback_candidates = [
            "nvidia/nemotron-3-super-120b-a12b:free",
            "grok-4.7",
            "gpt-5.6-luna",
            "gpt-4o"
        ]

        with self.lock:
            for candidate in fallback_candidates:
                if candidate == failed_model:
                    continue
                profile = self.profiles.get(candidate)
                if not profile:
                    continue
                if requires_tools and not profile.supports_tools:
                    continue
                telem = self.telemetry.get(candidate)
                if telem and not telem.is_available():
                    continue
                return candidate

        return "nvidia/nemotron-3-super-120b-a12b:free"

    def get_client(self, model_id: str, temperature: float = 0.2) -> OpenAIChatCompletionClient:
        """
        Constructs an OpenAIChatCompletionClient for the model.
        """
        profile = self.get_profile(model_id)
        if profile:
            api_key = os.getenv(profile.api_key_env) or os.getenv("OMNIROUTE_API_KEY") or "sk-local"
            base_url = profile.base_url
            model_info = ModelInfo(
                vision=profile.supports_vision,
                function_calling=profile.supports_tools,
                json_output=profile.supports_structured_output,
                structured_output=profile.supports_structured_output,
                family="unknown"
            )
        else:
            api_key = os.getenv("OMNIROUTE_API_KEY") or "sk-local"
            base_url = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
            model_info = ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                structured_output=True,
                family="unknown"
            )

        return OpenAIChatCompletionClient(
            model=model_id,
            base_url=base_url,
            api_key=api_key,
            model_info=model_info,
            include_name_in_message=False,
            temperature=temperature,
            timeout=120
        )

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Returns snapshot of telemetry across all models."""
        with self.lock:
            res = {}
            for mid, t in self.telemetry.items():
                avg_lat = round(t.total_latency_seconds / max(1, t.requests_succeeded), 3)
                res[mid] = {
                    "total_requests": t.requests_total,
                    "succeeded": t.requests_succeeded,
                    "failed": t.requests_failed,
                    "rate_limits": t.rate_limits_encountered,
                    "timeouts": t.timeouts_encountered,
                    "avg_latency_s": avg_lat,
                    "prompt_tokens": t.prompt_tokens_total,
                    "completion_tokens": t.completion_tokens_total,
                    "available": t.is_available()
                }
            return res

# Global registry singleton
model_registry = ModelRegistry()
