import os
from typing import ClassVar

from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding, BindingType
from textual.screen import Screen
from textual.widgets import Footer, Header, LoadingIndicator

from ical import ICal, ICalClient
from widgets import MainPane


class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()


class CalendarApp(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit app", show=True),
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
    ]
    CSS_PATH: ClassVar[str] = "main.css"
    SCREENS = {"loading_screen": LoadingScreen()}

    ical_client: ICalClient

    def compose(self) -> ComposeResult:
        self._setup()

        yield Header(show_clock=True)
        yield MainPane(self.ical_client)
        yield Footer()

    def action_toggledark(self) -> None:
        self.dark = not self.dark

    def on_loadable_widget_loading(self):
        self.push_screen("loading_screen")

    def on_loadable_widget_loaded(self):
        try:
            self.pop_screen()
        except ScreenStackError:
            pass

    def _setup(self):
        url = os.getenv("ICAL_URL", "")
        self.ical_client = ICal(url)


if __name__ == "__main__":
    app = CalendarApp()
    app.run()
