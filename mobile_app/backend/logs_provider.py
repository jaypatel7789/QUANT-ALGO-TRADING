"""
Shark MT5 Sentinel - Live Log Provider
Aggregates and formats live logs from:
1. MQL5 Expert Advisors (EA signals, trade executions, print statements)
2. MT5 Terminal (network, trade permissions, broker routing)
3. Sentinel Watcher (Algo Trading button toggles, news shield events)
4. Sentinel Security Audit
"""

import os
import glob
import re
from datetime import datetime

class LogsProvider:
    def __init__(self, data_path=None):
        self.data_path = data_path or self._find_mt5_data_path()
        self.watcher_log = r"C:\SharkSentinel\mt5_watcher.log"
        self.audit_log = os.path.join(os.path.dirname(__file__), "logs", "sentinel_audit.log")

    def _find_mt5_data_path(self):
        term_base = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal"
        if os.path.exists(term_base):
            for entry in os.listdir(term_base):
                p = os.path.join(term_base, entry)
                if os.path.isdir(p) and os.path.exists(os.path.join(p, "MQL5")):
                    return p
        return None

    def _read_file_lines(self, filepath, max_lines=250):
        if not filepath or not os.path.exists(filepath):
            return []
        
        # MT5 log files are utf-16 with BOM; other logs are utf-8
        for enc in ["utf-16", "utf-16-le", "utf-8", "latin-1"]:
            try:
                with open(filepath, "r", encoding=enc, errors="replace") as f:
                    lines = f.readlines()
                    # Filter out empty or whitespace lines
                    clean = [l.strip() for l in lines if l.strip()]
                    return clean[-max_lines:]
            except Exception:
                continue
        return []

    def _parse_mt5_line(self, line, default_source="TERMINAL"):
        """Parses MT5 tab-separated log line format: CODE \t ID \t TIME \t SOURCE \t MESSAGE"""
        parts = line.split("\t")
        if len(parts) >= 5:
            code, tid, time_str, mod, msg = parts[0], parts[1], parts[2], parts[3], "\t".join(parts[4:])
        elif len(parts) >= 4:
            code, tid, time_str, mod, msg = parts[0], parts[1], parts[2], "", parts[3]
        elif len(parts) >= 3:
            code, tid, time_str, mod, msg = parts[0], "", parts[1], "", parts[2]
        else:
            time_str = datetime.now().strftime("%H:%M:%S")
            mod = default_source
            msg = line

        # Classify Level
        msg_upper = msg.upper()
        if "TRADE OPEN" in msg_upper or "ORDER" in msg_upper or "DEAL" in msg_upper:
            level = "TRADE"
        elif "ERROR" in msg_upper or "FAILED" in msg_upper or "REJECTED" in msg_upper:
            level = "ERROR"
        elif "WARNING" in msg_upper or "ALERT" in msg_upper:
            level = "WARN"
        elif "DISABLED" in msg_upper:
            level = "WARN"
        elif "ENABLED" in msg_upper:
            level = "SUCCESS"
        else:
            level = "INFO"

        return {
            "time": time_str[:12],
            "source": default_source,
            "module": mod[:35] if mod else default_source,
            "level": level,
            "message": msg,
            "raw": line
        }

    def _parse_watcher_line(self, line):
        # Format: 2026-10-06 12:29:16 [INFO] [BUTTON TOGGLED] New Algo Button State: False
        match = re.match(r"^(\d{4}-\d{2}-\d{2}\s+)?(\d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.*)$", line)
        if match:
            time_str = match.group(2)
            lvl_raw = match.group(3).upper()
            msg = match.group(4)
        else:
            time_str = datetime.now().strftime("%H:%M:%S")
            lvl_raw = "INFO"
            msg = line

        level = "INFO"
        if "BUTTON TOGGLED" in msg.upper():
            level = "TRADE" if "TRUE" in msg.upper() else "WARN"
        elif "ERROR" in lvl_raw:
            level = "ERROR"
        elif "WARN" in lvl_raw:
            level = "WARN"

        return {
            "time": time_str,
            "source": "SENTINEL",
            "module": "ButtonWatcher",
            "level": level,
            "message": msg,
            "raw": line
        }

    def get_logs(self, category="all", limit=150, search=""):
        if not self.data_path:
            self.data_path = self._find_mt5_data_path()

        results = []

        # 1. MT5 Expert Logs (MQL5\Logs)
        if category in ["all", "experts"] and self.data_path:
            mql5_log_dir = os.path.join(self.data_path, "MQL5", "Logs")
            if os.path.exists(mql5_log_dir):
                files = sorted(glob.glob(os.path.join(mql5_log_dir, "*.log")), reverse=True)
                # Read today and yesterday if needed
                for f in files[:2]:
                    raw_lines = self._read_file_lines(f, max_lines=limit)
                    for l in raw_lines:
                        parsed = self._parse_mt5_line(l, default_source="EXPERTS")
                        results.append(parsed)

        # 2. MT5 Terminal Logs (Logs)
        if category in ["all", "terminal"] and self.data_path:
            term_log_dir = os.path.join(self.data_path, "Logs")
            if os.path.exists(term_log_dir):
                files = sorted(glob.glob(os.path.join(term_log_dir, "*.log")), reverse=True)
                for f in files[:2]:
                    raw_lines = self._read_file_lines(f, max_lines=limit)
                    for l in raw_lines:
                        parsed = self._parse_mt5_line(l, default_source="TERMINAL")
                        results.append(parsed)

        # 3. Sentinel Watcher Daemon Logs
        if category in ["all", "watcher", "sentinel"] and os.path.exists(self.watcher_log):
            raw_lines = self._read_file_lines(self.watcher_log, max_lines=limit)
            for l in raw_lines:
                results.append(self._parse_watcher_line(l))

        # Sort combined results by time string or keep natural latest
        # Filter by search keyword if provided
        if search:
            search_lower = search.lower()
            results = [
                r for r in results 
                if search_lower in r["message"].lower() 
                or search_lower in r["module"].lower() 
                or search_lower in r["source"].lower()
            ]

        # Slice to limit (most recent at bottom/chronological for streaming)
        sliced = results[-limit:]

        return {
            "total_count": len(results),
            "returned_count": len(sliced),
            "category": category,
            "data_path": self.data_path,
            "logs": sliced
        }

# Singleton
logs_provider = LogsProvider()
