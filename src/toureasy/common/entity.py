from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from toureasy.common.identity import Id

TModel = TypeVar("TModel")


class Entity(Generic[TModel]):
    """Base entity: identity-based equality plus audit timestamps.

    Timestamps are always passed in: the domain never reads the clock itself.
    """

    def __init__(
        self,
        entity_id: Id[TModel],
        created_at_utc: datetime,
        last_modified_at_utc: datetime,
    ) -> None:
        self._id = entity_id
        self._created_at_utc = created_at_utc
        self._last_modified_at_utc = last_modified_at_utc

    @property
    def id(self) -> Id[TModel]:
        return self._id

    @property
    def created_at_utc(self) -> datetime:
        return self._created_at_utc

    @property
    def last_modified_at_utc(self) -> datetime:
        return self._last_modified_at_utc

    def __eq__(self, other: object) -> bool:
        return type(other) is type(self) and isinstance(other, Entity) and other.id == self.id

    def __hash__(self) -> int:
        return hash((type(self), self._id))
