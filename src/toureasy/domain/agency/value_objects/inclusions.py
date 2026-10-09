from __future__ import annotations
from dataclasses import dataclass
from datetime import time

from toureasy.common.result import Result, success

@dataclass(frozen=True)
class Inclusions:
    included: tuple[str, ...]        # "what is included"
    excluded: tuple[str, ...]        # "what is NOT included"

    @classmethod
    def create(cls, included: list[str], excluded: list[str]) -> "Result[Inclusions]":
        inc = tuple(s.strip() for s in (included or []) if s and s.strip())
        exc = tuple(s.strip() for s in (excluded or []) if s and s.strip())
        return success(cls(inc, exc))   # both may be empty — no hard rule