from datetime import datetime
from typing import Protocol


class TimeProvider(Protocol):
    """Source of the current time. The domain receives ``now`` as an argument; services ask this port."""

    def now(self) -> datetime: ...
