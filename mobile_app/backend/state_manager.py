import os
import json
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOG_DIR = os.path.join(BASE_DIR, "logs")
STATE_FILE = os.path.join(CONFIG_DIR, "sentinel_state.json")
AUDIT_LOG_FILE = os.path.join(LOG_DIR, "sentinel_audit.log")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup rotating audit logger
logger = logging.getLogger("SentinelAudit")
logger.setLevel(logging.INFO)
if not logger.handlers:
    rfh = RotatingFileHandler(AUDIT_LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)
    # Also add console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class StateManager:
    def __init__(self):
        self.state = self.load_state()

    def get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def load_state(self) -> dict:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                logger.error(f"Failed to read state file: {e}. Using fallback defaults.")

        default_state = {
            "pin_hash": self.get_hash("7777"),
            "master_algo_enabled": True,
            "news_shield_enabled": True,
            "news_block_before_min": 30,
            "news_block_after_min": 15,
            "algo_states": {
                "11018": True, "21018": True, "14024": True, "24024": True,
                "14025": True, "14019": True, "14013": True, "11011": True,
                "11012": True, "100301": True, "100501": True, "100601": True,
                "100901": True, "101201": True, "101701": True, "9991212": True
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        self.save_state(default_state)
        return default_state

    def save_state(self, new_state: dict = None):
        if new_state:
            self.state = new_state
        self.state["last_updated"] = datetime.utcnow().isoformat()
        try:
            temp_file = STATE_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
            os.replace(temp_file, STATE_FILE)
        except Exception as e:
            logger.error(f"Failed to write state file: {e}")

    def verify_pin(self, entered_pin: str) -> bool:
        entered_hash = self.get_hash(entered_pin.strip())
        is_valid = (entered_hash == self.state.get("pin_hash"))
        if is_valid:
            logger.info("Security Gate: PIN verified successfully.")
        else:
            logger.warning("Security Gate: Invalid PIN attempt rejected.")
        return is_valid

    def update_pin(self, old_pin: str, new_pin: str) -> bool:
        if self.verify_pin(old_pin):
            self.state["pin_hash"] = self.get_hash(new_pin.strip())
            self.save_state()
            logger.info("Security Gate: Master PIN successfully updated.")
            return True
        return False

    def is_master_enabled(self) -> bool:
        return self.state.get("master_algo_enabled", True)

    def set_master_enabled(self, enabled: bool):
        self.state["master_algo_enabled"] = enabled
        self.save_state()
        logger.info(f"Policy: Master Algo Trading set to {'ENABLED' if enabled else 'FROZEN'}")

    def is_algo_enabled(self, magic: int) -> bool:
        magic_str = str(magic)
        return self.state.get("algo_states", {}).get(magic_str, True)

    def set_algo_enabled(self, magic: int, enabled: bool):
        if "algo_states" not in self.state:
            self.state["algo_states"] = {}
        self.state["algo_states"][str(magic)] = enabled
        self.save_state()
        logger.info(f"Policy: EA Magic #{magic} set to {'ENABLED' if enabled else 'PAUSED'}")

    def get_news_settings(self) -> dict:
        return {
            "enabled": self.state.get("news_shield_enabled", True),
            "block_before_min": self.state.get("news_block_before_min", 30),
            "block_after_min": self.state.get("news_block_after_min", 15)
        }

    def set_news_settings(self, enabled: bool, before: int, after: int):
        self.state["news_shield_enabled"] = enabled
        self.state["news_block_before_min"] = before
        self.state["news_block_after_min"] = after
        self.save_state()
        logger.info(f"Policy: News Shield updated: Enabled={enabled}, BlockBefore={before}m, BlockAfter={after}m")

# Global singleton
state_mgr = StateManager()
