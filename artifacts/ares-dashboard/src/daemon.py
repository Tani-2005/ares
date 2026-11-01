"""
ARES Background Pipeline Ingestion Daemon (PRD §1.3 & SRS FR-01).
Runs periodic delta ingestion jobs in a lightweight background thread,
updating SQLite master_data.db and logging execution metrics without blocking the UI.
"""

import threading
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_DAEMON_THREAD: Optional[threading.Thread] = None
_STOP_EVENT = threading.Event()
_DAEMON_STATE = {
    "is_running": False,
    "last_run_time": None,
    "interval_minutes": 360,
    "runs_completed": 0,
    "last_status": "IDLE"
}

def _daemon_worker(interval_seconds: int):
    global _DAEMON_STATE
    from pipeline import AresPipeline
    
    logger.info(f"ARES Background Daemon started. Interval: {interval_seconds}s")
    _DAEMON_STATE["is_running"] = True
    _DAEMON_STATE["last_status"] = "ACTIVE_MONITORING"
    
    pipeline = AresPipeline()
    
    while not _STOP_EVENT.is_set():
        try:
            logger.info("ARES Daemon triggering scheduled delta pipeline...")
            _DAEMON_STATE["last_status"] = "RUNNING_PIPELINE"
            res = pipeline.run_full_pipeline(force_static=False)
            _DAEMON_STATE["runs_completed"] += 1
            _DAEMON_STATE["last_run_time"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
            _DAEMON_STATE["last_status"] = "SUCCESS" if res.get("success") else "FAILED"
        except Exception as e:
            logger.error(f"Daemon pipeline run failed: {e}")
            _DAEMON_STATE["last_status"] = f"ERROR: {str(e)[:40]}"
            
        # Sleep in chunks to allow quick cancellation
        for _ in range(int(interval_seconds / 5)):
            if _STOP_EVENT.is_set():
                break
            time.sleep(5)
            
    _DAEMON_STATE["is_running"] = False
    _DAEMON_STATE["last_status"] = "STOPPED"
    logger.info("ARES Background Daemon stopped.")

def start_background_daemon(interval_minutes: int = 360) -> bool:
    """Starts the background ingestion thread if not already running."""
    global _DAEMON_THREAD, _STOP_EVENT, _DAEMON_STATE
    if _DAEMON_THREAD and _DAEMON_THREAD.is_alive():
        return False
        
    _STOP_EVENT.clear()
    _DAEMON_STATE["interval_minutes"] = interval_minutes
    interval_seconds = max(60, interval_minutes * 60)
    
    _DAEMON_THREAD = threading.Thread(
        target=_daemon_worker,
        args=(interval_seconds,),
        daemon=True,
        name="ARES_Ingestion_Daemon"
    )
    _DAEMON_THREAD.start()
    return True

def stop_background_daemon() -> bool:
    """Signals the background ingestion thread to stop."""
    global _STOP_EVENT
    _STOP_EVENT.set()
    return True

def get_daemon_status() -> Dict[str, Any]:
    """Returns current state of the background daemon."""
    global _DAEMON_STATE, _DAEMON_THREAD
    is_alive = bool(_DAEMON_THREAD and _DAEMON_THREAD.is_alive())
    _DAEMON_STATE["is_running"] = is_alive
    return dict(_DAEMON_STATE)

