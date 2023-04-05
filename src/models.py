from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    class NotFound(Exception):
        pass


class Event(BaseModel):
    summary: Optional[str]
    description: Optional[str]
    start: Optional[datetime]
    end: Optional[datetime]
    # self.uid = -1
    # self.summary = None
    # self.description = None
    # self.start = None
    # self.end = None
    # self.all_day = True
    # self.transparent = False
    # self.recurring = False
    # self.location = None
    # self.private = False
    # self.created = None
    # self.last_modified = None
    # self.sequence = None
    # self.recurrence_id = None
    # self.attendee = None
    # self.organizer = None
    # self.categories = None
    # self.floating = None
    # self.status = None
    # self.url = None

    class Config:
        orm_mode = True

    def covers_date(self, reference_date: date):
        if self.start is None or self.end is None:
            return False
        return self.start.date() <= reference_date and self.end.date() >= reference_date

    def is_in_range(self, date_range: tuple[date, date]):
        start, end = date_range
        if self.start is None:
            return False
        return self.start.date() >= start and self.start.date() <= end

    @property
    def short_description(self) -> str:
        if self.summary is None:
            return "No summary"
        return self.summary
