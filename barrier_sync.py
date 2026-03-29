#!/usr/bin/env python3
"""barrier_sync - Cyclic barrier for synchronizing N threads at a point."""
import sys, threading

class Barrier:
    def __init__(self, parties):
        self.parties = parties
        self._count = 0
        self._generation = 0
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
    def wait(self, timeout=None):
        with self._cond:
            gen = self._generation
            self._count += 1
            if self._count == self.parties:
                self._count = 0
                self._generation += 1
                self._cond.notify_all()
                return True
            while self._generation == gen:
                if not self._cond.wait(timeout):
                    raise TimeoutError("barrier timeout")
            return False

def test():
    b = Barrier(3)
    results = []
    lock = threading.Lock()
    def worker(wid):
        with lock: results.append(("before", wid))
        b.wait(timeout=5)
        with lock: results.append(("after", wid))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()
    befores = [r for r in results if r[0] == "before"]
    afters = [r for r in results if r[0] == "after"]
    assert len(befores) == 3
    assert len(afters) == 3
    print("barrier_sync: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: barrier_sync.py --test")
