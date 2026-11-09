from threading import Lock

class GenerateCounter:
    def __init__(self):
        self._generated = 0
        self._lock = Lock()

    def increase_generated(self):
        with self._lock:
            self._generated += 1

    def get_generated(self) -> int:
        return self._generated

generate_counter = GenerateCounter()