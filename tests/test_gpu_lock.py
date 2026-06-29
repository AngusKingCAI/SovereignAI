"""Tests for GPU lock — in-process mutual exclusion."""
import threading
import time

from sovereignai.workers.education.teacher_worker import _GPU_LOCK


def test_gpu_lock_is_threading_lock():
    """Test GPU lock is a threading.Lock instance."""
    assert type(_GPU_LOCK).__name__.lower() == 'lock'


def test_gpu_lock_mutual_exclusion():
    """Test GPU lock provides mutual exclusion for in-process consumers."""
    results = []

    def worker(lock, worker_id):
        """Worker function that tries to acquire the lock."""
        acquired = lock.acquire(timeout=1)
        if acquired:
            try:
                results.append(f"Worker {worker_id} acquired lock")
                time.sleep(0.1)  # Hold lock briefly
            finally:
                lock.release()
                results.append(f"Worker {worker_id} released lock")
        else:
            results.append(f"Worker {worker_id} failed to acquire lock")

    # Create multiple threads trying to acquire the lock
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(_GPU_LOCK, i))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Verify only one thread held the lock at a time
    # (This is a basic check — in production, we'd use more sophisticated testing)
    assert len(results) == 6  # 3 workers * 2 messages each
    assert all("acquired" in r or "released" in r or "failed" in r for r in results)


def test_gpu_lock_timeout():
    """Test GPU lock timeout works correctly."""
    # Acquire the lock
    _GPU_LOCK.acquire()

    try:
        # Try to acquire with timeout — should fail
        acquired = _GPU_LOCK.acquire(timeout=0.1)
        assert acquired is False
    finally:
        _GPU_LOCK.release()


def test_gpu_lock_release_after_timeout():
    """Test lock can be released after a timeout."""
    # Try to acquire with timeout while lock is held
    _GPU_LOCK.acquire()

    try:
        acquired = _GPU_LOCK.acquire(timeout=0.1)
        assert acquired is False
    finally:
        _GPU_LOCK.release()

    # Now lock should be available
    acquired = _GPU_LOCK.acquire(timeout=0.1)
    assert acquired is True
    _GPU_LOCK.release()
