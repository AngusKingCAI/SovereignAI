import threading
import time

from sovereignai.workers.education.teacher_worker import _GPU_LOCK


def test_gpu_lock_is_threading_lock():
    assert type(_GPU_LOCK).__name__.lower() == 'lock'

def test_gpu_lock_mutual_exclusion():
    results = []

    def worker(lock, worker_id):
        acquired = lock.acquire(timeout=1)
        if acquired:
            try:
                results.append(f'Worker {worker_id} acquired lock')
                time.sleep(0.1)
            finally:
                lock.release()
                results.append(f'Worker {worker_id} released lock')
        else:
            results.append(f'Worker {worker_id} failed to acquire lock')
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(_GPU_LOCK, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 6
    assert all('acquired' in r or 'released' in r or 'failed' in r for r in results)

def test_gpu_lock_timeout():
    _GPU_LOCK.acquire()
    try:
        acquired = _GPU_LOCK.acquire(timeout=0.1)
        assert acquired is False
    finally:
        _GPU_LOCK.release()

def test_gpu_lock_release_after_timeout():
    _GPU_LOCK.acquire()
    try:
        acquired = _GPU_LOCK.acquire(timeout=0.1)
        assert acquired is False
    finally:
        _GPU_LOCK.release()
    acquired = _GPU_LOCK.acquire(timeout=0.1)
    assert acquired is True
    _GPU_LOCK.release()
