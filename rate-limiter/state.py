from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class WindowCounterState:

    window_start: float = 0.0
    prev_count: int = 0
    curr_count: int = 0

    def __repr__(self) -> str:
        return (
            f"WindowCounterState(start={self.window_start:.4f}, "
            f"prev={self.prev_count}, curr={self.curr_count})"
        )
