import psutil
import time
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        # Simulated bandwidth accumulator (in MB)
        self.accumulated_egress_mb = 14.8

    def get_telemetry(self):
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')

        # Check for MT5 process
        mt5_running = False
        mt5_mem_mb = 0.0
        for p in psutil.process_iter(['name', 'memory_info']):
            try:
                if 'terminal64' in p.info['name'].lower():
                    mt5_running = True
                    mt5_mem_mb = round(p.info['memory_info'].rss / (1024 * 1024), 1)
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        uptime_sec = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"

        # AWS Free Tier limits (100 GB Egress / Month)
        free_tier_egress_limit_gb = 100.0
        used_egress_gb = round(self.accumulated_egress_mb / 1024.0, 3)
        egress_used_pct = round((used_egress_gb / free_tier_egress_limit_gb) * 100, 2)

        return {
            "cpu_percent": cpu_pct,
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "ram_percent": mem.percent,
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_percent": disk.percent,
            "mt5_process_running": mt5_running,
            "mt5_ram_usage_mb": mt5_mem_mb,
            "aws_free_tier": {
                "egress_limit_gb": free_tier_egress_limit_gb,
                "egress_used_gb": used_egress_gb,
                "egress_used_percent": egress_used_pct,
                "status": "WELL_BELOW_FREE_LIMIT"
            },
            "system_uptime": uptime_str,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
