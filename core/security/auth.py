"""
Dashboard Authentication & Origin Security Module
Enforces:
- Loopback-by-default binding
- Origin verification (prevents cross-site WebSocket hijacking & CSRF)
- Session token validation (cookie, header, or query param)
- Automatic local session cookie generation for practical browser UX
"""
import os
import secrets
from pathlib import Path
from typing import Optional, Set
from fastapi import Request, WebSocket, HTTPException, status
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TOKEN_FILE = BASE_DIR / ".local_session_token"

def get_or_create_session_token() -> str:
    """Retrieves or creates a secure local session token."""
    env_token = os.getenv("AGENT_API_TOKEN") or os.getenv("DASHBOARD_AUTH_TOKEN")
    if env_token and len(env_token.strip()) >= 8:
        return env_token.strip()

    if TOKEN_FILE.exists():
        try:
            token = TOKEN_FILE.read_text(encoding="utf-8").strip()
            if len(token) >= 16:
                return token
        except Exception:
            pass

    new_token = secrets.token_urlsafe(32)
    try:
        TOKEN_FILE.write_text(new_token, encoding="utf-8")
    except Exception:
        pass
    return new_token

SESSION_TOKEN = get_or_create_session_token()

ALLOWED_HOSTS: Set[str] = {
    "127.0.0.1",
    "localhost",
    "::1",
    "[::1]"
}

def is_loopback_client(host: Optional[str]) -> bool:
    """Checks if the client IP is on the local machine loopback."""
    if not host:
        return False
    return host in ALLOWED_HOSTS or host.startswith("127.")

def verify_origin(request_or_ws: Request | WebSocket) -> bool:
    """
    Validates that Origin or Referer header matches local loopback.
    Prevents DNS rebinding and cross-site request attacks.
    """
    origin = request_or_ws.headers.get("origin")
    referer = request_or_ws.headers.get("referer")
    header_val = origin or referer

    if not header_val:
        # Direct CLI / curl requests have no origin/referer; check client host
        client_host = request_or_ws.client.host if request_or_ws.client else None
        return is_loopback_client(client_host)

    # Clean protocol and path
    cleaned = (
        header_val.replace("http://", "")
        .replace("https://", "")
        .replace("ws://", "")
        .replace("wss://", "")
        .split("/")[0]
        .split(":")[0]
    )
    return cleaned in ALLOWED_HOSTS

def extract_token(request: Request) -> Optional[str]:
    """Extracts token from Header, Query, or Cookie."""
    # 1. Header: Authorization Bearer
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    # 2. Custom header
    custom_token = request.headers.get("x-session-token")
    if custom_token:
        return custom_token.strip()

    # 3. Cookie
    cookie_token = request.cookies.get("session_token")
    if cookie_token:
        return cookie_token.strip()

    # 4. Query param
    return request.query_params.get("token")

def require_auth(request: Request):
    """
    FastAPI dependency enforcing origin and session token verification.
    """
    if not verify_origin(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Untrusted request origin."
        )

    client_host = request.client.host if request.client else None
    token = extract_token(request)

    # For local loopback browser access, token is accepted if cookie matches or token matches
    if token and secrets.compare_digest(token, SESSION_TOKEN):
        return True

    # If it is a loopback client and session cookie is present, allow
    if is_loopback_client(client_host) and request.cookies.get("session_token") == SESSION_TOKEN:
        return True

    # Allow loopback direct requests if explicitly enabled by default for localhost dev
    if is_loopback_client(client_host) and not os.getenv("REQUIRE_STRICT_AUTH"):
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Valid session token or loopback cookie required."
    )

def verify_ws_auth(websocket: WebSocket) -> bool:
    """Verifies authentication for incoming WebSocket connections."""
    if not verify_origin(websocket):
        return False

    client_host = websocket.client.host if websocket.client else None
    token = websocket.query_params.get("token") or websocket.cookies.get("session_token")
    if token and secrets.compare_digest(token, SESSION_TOKEN):
        return True

    if is_loopback_client(client_host) and not os.getenv("REQUIRE_STRICT_AUTH"):
        return True

    return False
