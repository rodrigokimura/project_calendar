import os
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header

from ical import ICal, ICalClient
from widgets import MainPane


class CalendarApp(App):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit app", show=True),
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
    ]
    CSS_PATH: ClassVar[str] = "main.css"

    ical_client: ICalClient

    def compose(self) -> ComposeResult:
        self._setup()

        yield Header(show_clock=True)
        yield MainPane(self.ical_client)
        yield Footer()

    def action_toggledark(self) -> None:
        self.dark = not self.dark

    def _setup(self):
        url = os.getenv("ICAL_URL", "")
        self.ical_client = ICal(url)
