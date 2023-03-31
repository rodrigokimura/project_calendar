from typing import ClassVar

from dotenv import load_dotenv
from textual.app import App, ComposeResult, log
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header

from colors import kanagawa
from utils import generate_css_vars_from_colorscheme
from widgets import MainPane


class CalendarApp(App):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit app", show=True),
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
    ]
    DEFAULT_CSS = generate_css_vars_from_colorscheme(kanagawa)
    CSS_PATH: ClassVar[str] = "main.css"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield MainPane()
        yield Footer()

    def action_toggledark(self) -> None:
        self.dark = not self.dark


if __name__ == "__main__":
    load_dotenv()
    app = CalendarApp()
    app.run()
