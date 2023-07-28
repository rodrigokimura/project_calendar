from __future__ import annotations

from datetime import date, timedelta
from functools import wraps
from typing import Callable, ClassVar

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive, var
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

from constants import Direction
from ical import ICalClient
from models import Event
from utils import (
    format_date,
    get_final_date_of_monthly_calendar,
    get_initial_date_of_monthly_calendar,
    get_today,
    get_weekday_names,
)


class LoadableWidget(Widget):
    class Loading(Message):
        ...

    class Loaded(Message):
        ...

    @classmethod
    def show_loading_animation(cls, method: Callable):
        error = ValueError(
            f"{method.__name__} should be an instance method of a {cls.__name__} subclass."
        )

        @wraps(method)
        def wrapper_func(*args, **kwargs):
            if len(args) == 0:
                raise error
            loadable_widget = args[0]
            if not isinstance(loadable_widget, LoadableWidget):
                raise error

            loadable_widget.post_message(loadable_widget.Loading())

            method(*args, **kwargs)

            loadable_widget.post_message(loadable_widget.Loaded())

        return wrapper_func


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


class Month(Container, LoadableWidget):
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
        Binding("l", "move_right", "Right", show=True),
        Binding("h", "move_left", "Left", show=True),
        Binding("j", "move_down", "Down", show=True),
        Binding("k", "move_up", "Up", show=True),
        Binding("space", "select", "Select", show=True),
    ]
    can_focus = True
    month = var(lambda: get_today().month)
    year = var(lambda: get_today().year)
    header = var(MonthlyCalendarHeader)
    highlighted_date = var(lambda: get_today())

    def __init__(self, ical_client: ICalClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ical_client = ical_client

    def compose(self) -> ComposeResult:
        yield self.header
        self.container = Container()
        with self.container:
            for wd in get_weekday_names():
                yield Static(wd, classes="weekday-name-header")
        self._load_data()

    @LoadableWidget.show_loading_animation
    def _load_data(self):
        first_day_of_month = date(self.year, self.month, 1)
        initial_date = get_initial_date_of_monthly_calendar(self.year, self.month)
        final_date = get_final_date_of_monthly_calendar(self.year, self.month)

        self.header.reference_date = first_day_of_month

        self.container.query(Day).remove()

        for i in range((final_date - initial_date).days + 1):
            day = Day()
            reference_date = initial_date + timedelta(days=i)
            day.reference_month = self.month
            day.reference_date = reference_date
            self.container.mount(day)
        self._load_events()

    def _load_events(self):
        for day in self.container.query(Day):
            day.events = self.ical_client.get_events_by_day(day.reference_date)

    def action_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.year -= 1
            self.month = 12

    def action_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.year += 1
            self.month = 1

    def action_move_right(self):
        self._move(Direction.RIGHT)

    def action_move_left(self):
        self._move(Direction.LEFT)

    def action_move_up(self):
        self._move(Direction.UP)

    def action_move_down(self):
        self._move(Direction.DOWN)

    def action_select(self):
        for day in self.container.query(Day):
            if day.reference_date == self.highlighted_date:
                self.app.push_screen(EventsModal(day.events))

    def watch_month(self, /):
        self._load_data()

    def watch_highlighted_date(self, _, new: date):
        for day in self.container.query(Day):
            if new == day.reference_date:
                self._highlight(new)
                break
        else:
            self.month = new.month
            self.year = new.year
            self._highlight(new)

    def _move(self, direction: Direction):
        offsets = {
            Direction.RIGHT: 1,
            Direction.LEFT: -1,
            Direction.DOWN: 7,
            Direction.UP: -7,
        }
        _date = self.highlighted_date + timedelta(days=offsets[direction])
        self.highlighted_date = _date

    def _highlight(self, which: date):
        class_name = "highlighted"

        try:
            day = self.container.query_one(f".{class_name}", Day)
            day.remove_class(class_name)
        except NoMatches:
            pass

        for day in self.container.query(Day):
            if day.reference_date == which:
                day.add_class(class_name)


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

    def watch_reference_date(self, /):
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


class EventList(ListView):
    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("page_down", "page_down", "Page Down", show=False),
        Binding("page_up", "page_up", "Page Up", show=False),
    ]


class EventsModal(ModalScreen[str]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "quit", "Quit", show=True),
    ]

    def __init__(
        self,
        events: list[Event],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.events = events
        self.panel = EventPanel(events[0], classes="panel")

    def compose(self) -> ComposeResult:
        with Horizontal():
            event_list = EventList(
                *(
                    ListItem(Label(e.short_description, classes="event"))
                    for e in self.events
                )
            )
            event_list.focus()
            yield event_list
            yield self.panel

    def action_quit(self):
        self.app.pop_screen()

    def on_list_view_highlighted(self, event: EventList.Highlighted):
        idx = event.list_view.index
        if idx is not None:
            event_ = self.events[idx]
            self.panel.event = event_


class EventPanel(VerticalScroll):
    event = var(lambda: Event())
    title: Label = Label()
    description: Label = Label()
    start: Label = Label()
    end: Label = Label()

    def __init__(
        self,
        event: Event,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.event = event
        self.title = Label(self.event.summary or "")
        self.description = Label(self.event.description or "")
        self.start = Label(format_date(self.event.start) or "")
        self.end = Label(format_date(self.event.end) or "")

    def compose(self) -> ComposeResult:
        self.update()
        yield self.title
        yield self.start
        yield self.end
        yield self.description

    def update(self):
        self.title.update(self.event.summary or "")
        self.description.update(self.event.description or "")
        self.start.update(format_date(self.event.start) or "")
        self.end.update(format_date(self.event.end) or "")

    def watch_event(self, /):
        self.update()
