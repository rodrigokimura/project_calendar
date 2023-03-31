from __future__ import annotations

from datetime import date, timedelta
from typing import ClassVar

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container
from textual.reactive import reactive, var
from textual.widget import Widget
from textual.widgets import Static

from utils import get_today, get_weekday_names


class MonthlyCalendarHeader(Widget):
    DEFAULT_CSS = """
    MonthlyCalendarHeader {
        height: auto;
        padding: 1;
        align: center middle;
        text-align: center;
    }
    """
    reference_date = reactive(get_today)
    format = reactive("%B %Y")

    def render(self):
        return self.reference_date.strftime(self.format)


class MainPane(Container):
    current_month: int
    current_year: int

    def compose(self) -> ComposeResult:
        m = Month()
        yield m
        m.focus()

    def action_quit_app(self):
        self.app.exit()


class Month(Container):
    DEFAULT_CSS = """
    Month {
        layout: vertical;
    }
    Month > Container {
        layout: grid;
        grid-size: 7 6;
        grid-rows: 1 1fr 1fr 1fr 1fr 1fr;
    }
    Month > Container > Static {
        text-align: center;
    }
    """
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("n", "next", "Next month", show=True),
        Binding("p", "prev", "Previous month", show=True),
    ]
    can_focus = True
    month = var(lambda: get_today().month)
    year = var(lambda: get_today().year)
    header = var(MonthlyCalendarHeader)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = [Day() for _ in range(7 * 5)]
        self.weekdays = ("sunday", "monday", "tuesday", "wednesday")

    def compose(self) -> ComposeResult:
        self._load_data()
        yield self.header
        with Container():
            for wd in get_weekday_names():
                yield Static(wd, classes="weekday-name-header")
            for d in self.days:
                yield d

    def _load_data(self):
        first_day_of_month = date(self.year, self.month, 1)
        week_of_first_day = first_day_of_month.isocalendar().week
        initial_date = date.fromisocalendar(
            self.year, week_of_first_day, 1
        ) - timedelta(days=1)

        self.header.reference_date = first_day_of_month

        for i, d in enumerate(self.days):
            d.reference_date = initial_date + timedelta(days=i)
            d.reference_month = self.month

    def action_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        self.refresh()

    def action_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
        self.refresh()

    def watch_month(self, old_month: int, new_month: int):
        self._load_data()


class Day(Widget):
    DEFAULT_CSS = """
    Day {
        height: 100%;
        border: solid gray;
    }
    """
    reference_date = reactive(get_today)
    reference_month = var(lambda: get_today().month)

    def render(self) -> RenderableType:
        self.renderable = str(self.reference_date.day)

        css_class_to_attr_map = {
            "today": self.is_today(),
            "saturday": self.is_saturday(),
            "sunday": self.is_sunday(),
            "current-month": self.is_current_month(),
        }
        for css_class, check in css_class_to_attr_map.items():
            (self.add_class if check else self.remove_class)(css_class)

        return f"{self.reference_date.day}"

    def is_current_month(self):
        if self.reference_date is None:
            return False
        return self.reference_date.month == self.reference_month

    def is_sunday(self):
        return self.reference_date.weekday() == 6

    def is_saturday(self):
        return self.reference_date.weekday() == 5

    def is_today(self):
        return self.reference_date == get_today()
