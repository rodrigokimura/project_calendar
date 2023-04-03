from __future__ import annotations

from datetime import date, timedelta
from typing import ClassVar

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical, VerticalScroll
from textual.reactive import reactive, var
from textual.widget import Widget
from textual.widgets import Label, Static

from ical import ICalClient
from models import Event
from utils import (
    get_final_date_of_monthly_calendar,
    get_initial_date_of_monthly_calendar,
    get_today,
    get_weekday_names,
)


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
    def __init__(
        self,
        ical_client: ICalClient,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.ical_client = ical_client
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def compose(self) -> ComposeResult:
        m = Month(self.ical_client)
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
        grid-size: 7;
        grid-rows: 1 1fr 1fr 1fr 1fr 1fr 1fr;
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

    def __init__(self, ical_client: ICalClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.days = [Day() for _ in range(7 * 4)]
        self.ical_client = ical_client

    def compose(self) -> ComposeResult:
        yield self.header
        self.container = Container()
        with self.container:
            for wd in get_weekday_names():
                yield Static(wd, classes="weekday-name-header")
        self._load_data()

    def _load_data(self):
        # TODO: add loading animation
        first_day_of_month = date(self.year, self.month, 1)
        initial_date = get_initial_date_of_monthly_calendar(self.year, self.month)
        final_date = get_final_date_of_monthly_calendar(self.year, self.month)

        self.header.reference_date = first_day_of_month

        self.container.query("Day").remove()

        for i in range((final_date - initial_date).days + 1):
            d = Day()
            reference_date = initial_date + timedelta(days=i)
            d.events = self.ical_client.get_events_by_day(reference_date)
            d.reference_month = self.month
            d.reference_date = reference_date
            self.container.mount(d)

    def action_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.year -= 1
            self.month = 12
        self.refresh()

    def action_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.year += 1
            self.month = 1
        self.refresh()

    def watch_month(self, old_month: int, new_month: int):
        self._load_data()


class DayText(Widget):
    DEFAULT_CSS = """
    DayText {
        height: 1;
        dock: top;
    }
    """
    reference_date = reactive(get_today)

    def render(self) -> RenderableType:
        self.renderable = str(self.reference_date.day)
        return f"{self.reference_date.day}"


class Day(Vertical):
    DEFAULT_CSS = """
    Day {
        border: solid gray;
    }
    """
    events: list[Event] = []
    events_container: VerticalScroll = VerticalScroll()
    reference_month = var(lambda: get_today().month)
    reference_date = var(get_today)
    day_text: DayText = DayText()

    def compose(self) -> ComposeResult:
        self.day_text = DayText()
        self.day_text.reference_date = self.reference_date
        yield self.day_text
        self.events_container = VerticalScroll(*self._get_event_labels())
        yield self.events_container

    def watch_reference_date(self, old: date, new: date):
        css_class_to_attr_map = {
            "today": self.is_today(),
            "saturday": self.is_saturday(),
            "sunday": self.is_sunday(),
            "current-month": self.is_current_month(),
        }
        for css_class, check in css_class_to_attr_map.items():
            (self.add_class if check else self.remove_class)(css_class)

        self.day_text.reference_date = self.reference_date
        self.events_container.query("Label").remove()
        self.events_container.mount_all(self._get_event_labels())

    def _get_event_labels(self):
        return (Label(ev.short_description, classes="event") for ev in self.events)

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
