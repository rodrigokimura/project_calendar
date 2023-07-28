from abc import ABC, abstractmethod
from datetime import date, timedelta
from functools import lru_cache
from typing import Optional

from icalevents.icalevents import events

from models import Event
from utils import get_last_day_of_month, get_ttl_hash


class ICalClient(ABC):
    url: str

    def __init__(self, url: str) -> None:
        self.url = url

    @abstractmethod
    def get_events_by_month(
        self, year: int, month: int, ttl_hash: Optional[int] = None
    ) -> list[Event]:
        pass

    @abstractmethod
    def get_events_by_day(self, reference_date: date) -> list[Event]:
        pass


class ICal(ICalClient):
    @lru_cache()
    def get_all_events(self, ttl_hash: Optional[int] = None):
        del ttl_hash  # HACK: emulate ttl on lru_cache

        start = date.today() - timedelta(days=365)
        end = date.today() + timedelta(days=365)

        return [Event.from_orm(e) for e in events(self.url, start=start, end=end)]

    def get_events_by_month(self, year: int, month: int):
        first_day_of_month = date(year, month, 1)
        last_day_of_month = get_last_day_of_month(year, month)

        events = self.get_all_events(get_ttl_hash())
        return [
            e for e in events if e.is_in_range((first_day_of_month, last_day_of_month))
        ]

    def get_events_by_day(self, reference_date: date) -> list[Event]:
        events = self.get_events_by_month(
            reference_date.year,
            reference_date.month,
        )
        events = [e for e in events if e.covers_date(reference_date)]
        events.sort(key=lambda e: e.start or 0)
        return events
