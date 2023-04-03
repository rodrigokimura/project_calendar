from abc import ABC, abstractmethod
from datetime import date, timedelta
from functools import lru_cache
from typing import Optional

from models import Event
from utils import get_ttl_hash


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
    def get_events_by_month(self, year: int, month: int, ttl_hash: None):
        del ttl_hash
        from icalevents.icalevents import events

        first_day_of_month = date(year, month, 1)
        last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)

        return [
            Event.from_orm(e)
            for e in events(self.url, start=first_day_of_month, end=last_day_of_month)
        ]

    def get_events_by_day(self, reference_date: date) -> list[Event]:
        events = self.get_events_by_month(
            reference_date.year, reference_date.month, get_ttl_hash()
        )
        return [e for e in events if e.covers_date(reference_date)]
