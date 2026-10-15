import time
import secrets
from fastapi import HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from state_manager import state_mgr, logger

security = HTTPBearer(auto_error=False)

import os
import json

SESSION_FILE = os.path.join(os.path.dirname(__file__), "config", "active_sessions.json")
SESSION_EXPIRATION_SECONDS = 86400 * 7  # 7 Days

def load_sessions():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_sessions(sessions):
    try:
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f)
    except Exception:
        pass

ACTIVE_SESSIONS = load_sessions()

# Rate limiter: ip -> { "failed_count": count, "locked_until": ts }
LOGIN_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes lockout

class AuthManager:
    @staticmethod
    def get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    @classmethod
    def check_rate_limit(cls, ip: str):
        now = time.time()
        record = LOGIN_ATTEMPTS.get(ip)
        if record and record.get("locked_until", 0) > now:
            remaining = int(record["locked_until"] - now)
            logger.warning(f"RateLimit: IP {ip} is locked out for another {remaining}s.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Security Lockout: Too many failed PIN attempts. Try again in {remaining} seconds."
            )

    @classmethod
    def register_failure(cls, ip: str):
        now = time.time()
        record = LOGIN_ATTEMPTS.setdefault(ip, {"failed_count": 0, "locked_until": 0})
        record["failed_count"] += 1
        if record["failed_count"] >= MAX_FAILED_ATTEMPTS:
            record["locked_until"] = now + LOCKOUT_DURATION_SECONDS
            logger.critical(f"Security Alert: IP {ip} exceeded {MAX_FAILED_ATTEMPTS} failed attempts. Locked out for 5 minutes!")
        else:
            logger.warning(f"Security: Failed PIN attempt #{record['failed_count']} from IP {ip}")

    @classmethod
    def reset_failure(cls, ip: str):
        if ip in LOGIN_ATTEMPTS:
            del LOGIN_ATTEMPTS[ip]

    @classmethod
    def authenticate_pin(cls, pin: str, ip: str) -> dict:
        cls.check_rate_limit(ip)
        if not state_mgr.verify_pin(pin):
            cls.register_failure(ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Master Security PIN."
            )

        cls.reset_failure(ip)
        token = secrets.token_hex(32)
        ACTIVE_SESSIONS[token] = {
            "created_at": time.time(),
            "ip": ip
        }
        save_sessions(ACTIVE_SESSIONS)
        logger.info(f"Auth Success: Session token issued to IP {ip}")
        return {"status": "SUCCESS", "token": token, "expires_in": SESSION_EXPIRATION_SECONDS}

    @classmethod
    def validate_token(cls, token: str) -> bool:
        if not token:
            return False
        session = ACTIVE_SESSIONS.get(token)
        if not session:
            return False
        if time.time() - session["created_at"] > SESSION_EXPIRATION_SECONDS:
            del ACTIVE_SESSIONS[token]
            save_sessions(ACTIVE_SESSIONS)
            return False
        return True

async def require_auth(request: Request, creds: HTTPAuthorizationCredentials = Security(security)):
    # 1. Check Bearer Token in Header
    token = creds.credentials if creds else None

    # 2. Check Query Param (for WebSockets or fallback)
    if not token:
        token = request.query_params.get("token")

    if not token or not AuthManager.validate_token(token):
        logger.warning(f"Unauthorized API request blocked: {request.method} {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or unauthorized. Please re-enter your Security PIN."
        )
    return token
