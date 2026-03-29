#!/usr/bin/env python3
"""Barrier synchronization primitive."""
import threading

class Barrier:
    def __init__(self, parties: int):
        if parties < 1:
            raise ValueError("parties must be >= 1")
        self.parties = parties
        self._count = 0
        self._generation = 0
        self._lock = threading.Lock()
        self._event = threading.Event()

    def wait(self, timeout: float = 5.0) -> int:
        with self._lock:
            gen = self._generation
            self._count += 1
            idx = self._count - 1
            if self._count == self.parties:
                self._count = 0
                self._generation += 1
                self._event.set()
                self._event = threading.Event()
                return idx
        event = self._event
        event.wait(timeout)
        return idx

    def reset(self):
        with self._lock:
            self._count = 0
            self._generation += 1
            self._event.set()
            self._event = threading.Event()

class CyclicBarrier:
    def __init__(self, parties: int, action=None):
        self.parties = parties
        self.action = action
        self._barrier = Barrier(parties)
        self._action_lock = threading.Lock()

    def wait(self, timeout=5.0) -> int:
        idx = self._barrier.wait(timeout)
        if idx == self.parties - 1 and self.action:
            with self._action_lock:
                self.action()
        return idx

def test():
    b = Barrier(3)
    results = [None] * 3
    def worker(i):
        results[i] = b.wait()
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert all(r is not None for r in results), f"Some threads didn't complete: {results}"
    # Cyclic with action
    action_count = [0]
    cb = CyclicBarrier(2, action=lambda: action_count.__setitem__(0, action_count[0] + 1))
    def cyc_worker():
        cb.wait()
    ts = [threading.Thread(target=cyc_worker) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join(timeout=5)
    assert action_count[0] == 1
    print("  barrier_sync: ALL TESTS PASSED")

if __name__ == "__main__":
    test()
