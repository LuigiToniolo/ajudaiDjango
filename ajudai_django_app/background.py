from concurrent.futures import ThreadPoolExecutor
import atexit


# Single worker to serialize all background DB operations - prevents SQLite lock contention.
# SQLite doesn't handle concurrent writes well, so processing messages one at a time is safer.
_executor = ThreadPoolExecutor(max_workers=1)


def submit(fn, *args, **kwargs):
    """Submit a callable to run in the background thread pool.

    Returns a Future for optional inspection, but callers typically ignore it.
    """
    return _executor.submit(fn, *args, **kwargs)


def _shutdown_executor():
    # Do not wait indefinitely on shutdown during process exit.
    _executor.shutdown(wait=False)


atexit.register(_shutdown_executor)


