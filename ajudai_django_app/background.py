from concurrent.futures import ThreadPoolExecutor
import atexit


# Small fixed-size executor suitable for low-traffic background work in WSGI.
# Keep the pool size conservative to avoid exhausting threads per process.
_executor = ThreadPoolExecutor(max_workers=2)


def submit(fn, *args, **kwargs):
    """Submit a callable to run in the background thread pool.

    Returns a Future for optional inspection, but callers typically ignore it.
    """
    return _executor.submit(fn, *args, **kwargs)


def _shutdown_executor():
    # Do not wait indefinitely on shutdown during process exit.
    _executor.shutdown(wait=False)


atexit.register(_shutdown_executor)


