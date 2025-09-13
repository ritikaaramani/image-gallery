# backend/run_worker.py
"""
Cross-platform RQ worker launcher. Ensures project root is on sys.path so
"backend.*" imports succeed regardless of working directory.
"""
import os
import sys
from pathlib import Path
import logging
from redis import Redis

# ensure project root (the folder that contains 'backend') is on sys.path
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[1]  # parent of 'backend' folder
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # rq imports
    from rq.queue import Queue
    # SimpleWorker / Worker for cross-platform
    from rq.worker import SimpleWorker, Worker
except Exception:
    from rq import Queue
    from rq.worker import SimpleWorker, Worker  # type: ignore

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
QUEUE_NAME = os.getenv("RQ_QUEUE", "generations")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("run_worker")

def main():
    log.info("Project root added to sys.path: %s", PROJECT_ROOT)
    log.info("Connecting to Redis at %s", REDIS_URL)
    redis_conn = Redis.from_url(REDIS_URL)

    q = Queue(QUEUE_NAME, connection=redis_conn)
    log.info("Queue '%s' ready (len=%s)", QUEUE_NAME, q.count)

    use_simple = sys.platform.startswith("win")
    if use_simple:
        log.info("Platform is Windows; using SimpleWorker (no fork).")
        worker = SimpleWorker([q], connection=redis_conn)
    else:
        try:
            worker = Worker([q], connection=redis_conn)
            log.info("Using normal Worker (may fork for job isolation).")
        except Exception as e:
            log.warning("Failed to instantiate Worker, falling back to SimpleWorker: %s", e)
            worker = SimpleWorker([q], connection=redis_conn)

    try:
        log.info("Starting worker (CTRL-C to quit). Listening on queue: %s", QUEUE_NAME)
        worker.work()
    except KeyboardInterrupt:
        log.info("Worker stopped by user")
    except Exception as exc:
        log.exception("Worker crashed: %s", exc)

if __name__ == "__main__":
    main()
