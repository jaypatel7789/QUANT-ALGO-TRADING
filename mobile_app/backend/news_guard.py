import time
import urllib.request
import json
from datetime import datetime, timedelta, timezone

from state_manager import state_mgr, logger

IST = timezone(timedelta(hours=5, minutes=30), name="IST")

def parse_event_datetime(dt_str: str):
    """
    Parses event datetime string from ForexFactory (ISO format with timezone offset e.g. -04:00)
    or fallback naive format, returning (dt_utc, dt_ist).
    """
    if not dt_str:
        now_u = datetime.now(timezone.utc)
        return now_u, now_u.astimezone(IST)
    if "T" in dt_str:
        try:
            aware_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return aware_dt.astimezone(timezone.utc), aware_dt.astimezone(IST)
        except Exception:
            pass
    try:
        naive = datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
        dt_utc = naive.replace(tzinfo=timezone.utc)
        return dt_utc, dt_utc.astimezone(IST)
    except Exception:
        now_u = datetime.now(timezone.utc)
        return now_u, now_u.astimezone(IST)

def format_countdown(diff_mins: float, block_after: int) -> str:
    if diff_mins > 1440:
        return f"In {int(diff_mins // 1440)}d {int((diff_mins % 1440) // 60)}h"
    elif diff_mins > 60:
        return f"In {int(diff_mins // 60)}h {int(diff_mins % 60)}m"
    elif diff_mins > 0:
        return f"In {int(diff_mins)} min"
    elif -block_after <= diff_mins <= 0:
        return f"ACTIVE ({abs(int(diff_mins))}m passed)"
    elif diff_mins >= -180:
        return f"Passed {abs(int(diff_mins))}m ago"
    else:
        return "Completed"


class NewsGuard:
    def __init__(self, mt5_bridge=None):
        self.mt5_bridge = mt5_bridge
        self.currencies = ["USD", "EUR", "GBP"]
        self.cached_events = []
        self.last_fetch_time = 0
        self.cache_ttl_seconds = 1800  # 30 minutes cache for freshest news data
        self.fetch_live_calendar()

    def set_bridge(self, bridge):
        self.mt5_bridge = bridge

    def fetch_live_calendar(self):
        now_ts = time.time()
        if self.cached_events and (now_ts - self.last_fetch_time < self.cache_ttl_seconds):
            return self.cached_events

        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    raw_data = json.loads(resp.read().decode("utf-8"))
                    parsed = []
                    for ev in raw_data:
                        country = ev.get("country", "").upper()
                        impact = ev.get("impact", "")
                        # Filter for high impact USD, EUR, GBP
                        if country in self.currencies and impact.lower() == "high":
                            dt_str = ev.get("date", "")
                            dt_utc, dt_ist = parse_event_datetime(dt_str)
                            parsed.append({
                                "id": ev.get("title", "") + dt_str,
                                "title": ev.get("title", "High-Impact Event"),
                                "currency": country,
                                "impact": "HIGH",
                                "time_raw": dt_str,
                                "time_ist": dt_ist.strftime("%d %b, %I:%M %p IST"),
                                "time_utc": dt_utc.strftime("%d %b, %H:%M UTC"),
                                "time_display": f"{dt_ist.strftime('%I:%M %p IST')} ({dt_utc.strftime('%H:%M UTC')})",
                                "time": dt_ist.strftime("%d %b, %I:%M %p IST"),
                                "timestamp_utc": int(dt_utc.timestamp()),
                                "forecast": ev.get("forecast", "-"),
                                "previous": ev.get("previous", "-")
                            })
                    if parsed:
                        self.cached_events = parsed
                        self.last_fetch_time = now_ts
                        logger.info(f"[NewsGuard] Loaded {len(parsed)} live High-Impact macroeconomic events from ForexFactory.")
                        return self.cached_events
        except Exception as e:
            logger.warning(f"[NewsGuard] ForexFactory network notice ({e}), using scheduled baseline.")

        if not self.cached_events:
            self.cached_events = self._generate_fallback_events()
        return self.cached_events

    def _generate_fallback_events(self):
        now_utc = datetime.now(timezone.utc)
        items = [
            ("US Non-Farm Payrolls (NFP)", "USD", timedelta(hours=6), "180K", "142K"),
            ("US FOMC Rate Decision & Press Conference", "USD", timedelta(days=2, hours=4), "5.00%", "5.25%"),
            ("ECB Monetary Policy Statement", "EUR", timedelta(days=3, hours=1), "3.65%", "3.65%"),
            ("BOE Official Bank Rate Decision", "GBP", timedelta(days=4, hours=2), "5.00%", "5.00%")
        ]
        out = []
        for title, cur, delta, fcast, prev in items:
            dt_utc = now_utc + delta
            dt_ist = dt_utc.astimezone(IST)
            out.append({
                "id": title,
                "title": title,
                "currency": cur,
                "impact": "HIGH",
                "time_raw": dt_utc.isoformat(),
                "time_ist": dt_ist.strftime("%d %b, %I:%M %p IST"),
                "time_utc": dt_utc.strftime("%d %b, %H:%M UTC"),
                "time_display": f"{dt_ist.strftime('%I:%M %p IST')} ({dt_utc.strftime('%H:%M UTC')})",
                "time": dt_ist.strftime("%d %b, %I:%M %p IST"),
                "timestamp_utc": int(dt_utc.timestamp()),
                "forecast": fcast,
                "previous": prev
            })
        return out

    def check_shield_status(self):
        events = self.fetch_live_calendar()
        settings = state_mgr.get_news_settings()
        shield_enabled = settings["enabled"]
        block_before = settings["block_before_min"]
        block_after = settings["block_after_min"]

        shield_active = False
        active_event_title = ""
        now_utc = datetime.now(timezone.utc)
        now_ist = now_utc.astimezone(IST)

        enriched_events = []
        for ev in events:
            try:
                dt_raw = ev.get("time_raw") or ev.get("time") or ""
                dt_utc, dt_ist = parse_event_datetime(dt_raw)
                diff_minutes = (dt_utc - now_utc).total_seconds() / 60.0

                countdown = format_countdown(diff_minutes, block_after)
                is_in_blackout = (-block_after <= diff_minutes <= block_before)

                if shield_enabled and is_in_blackout and not shield_active:
                    shield_active = True
                    active_event_title = f"{ev.get('currency')} {ev.get('title')}"

                ev_copy = dict(ev)
                ev_copy["time_ist"] = dt_ist.strftime("%d %b, %I:%M %p IST")
                ev_copy["time_utc"] = dt_utc.strftime("%d %b, %H:%M UTC")
                ev_copy["time_display"] = f"{dt_ist.strftime('%I:%M %p IST')} ({dt_utc.strftime('%H:%M UTC')})"
                ev_copy["countdown"] = countdown
                ev_copy["diff_minutes"] = round(diff_minutes, 1)
                ev_copy["in_blackout"] = is_in_blackout
                enriched_events.append(ev_copy)
            except Exception:
                enriched_events.append(ev)

        # Sort events: upcoming first, then recent
        enriched_events.sort(key=lambda x: x.get("diff_minutes", 999999))
        # Keep non-expired or recently passed events
        active_view_events = [e for e in enriched_events if e.get("diff_minutes", 0) >= -180]
        if not active_view_events:
            active_view_events = enriched_events

        # Sync state with MT5 bridge
        if self.mt5_bridge:
            if self.mt5_bridge.news_shield_blocking != shield_active:
                self.mt5_bridge.news_shield_blocking = shield_active
                self.mt5_bridge.sync_terminal_global_variables()
                if shield_active:
                    logger.warning(f"[NEWS SHIELD ACTIVE] Trading blocked for: {active_event_title}")
                else:
                    logger.info("[NEWS SHIELD STAND-BY] Blackout window cleared.")

        return {
            "shield_enabled": shield_enabled,
            "shield_active": shield_active,
            "active_event": active_event_title,
            "block_before_min": block_before,
            "block_after_min": block_after,
            "server_time_ist": now_ist.strftime("%d %b %Y, %I:%M:%S %p IST"),
            "server_time_utc": now_utc.strftime("%d %b %Y, %H:%M:%S UTC"),
            "server_tz": "IST (UTC+05:30)",
            "upcoming_events": active_view_events[:8]
        }

    def update_settings(self, enabled: bool, block_before_min: int, block_after_min: int):
        state_mgr.set_news_settings(enabled, block_before_min, block_after_min)
        if self.mt5_bridge:
            if not enabled:
                self.mt5_bridge.news_shield_blocking = False
                logger.info("[NEWS SHIELD DISABLED] News shield turned OFF by user. All trading unblocked.")
            else:
                self.check_shield_status()
            self.mt5_bridge.sync_terminal_global_variables()
        return {
            "status": "SUCCESS",
            "shield_enabled": enabled,
            "block_before_min": block_before_min,
            "block_after_min": block_after_min
        }

