"""Aplicação Textual do StockWatch."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header


class StockWatchApp(App[None]):
    """Ponto de entrada da TUI."""

    TITLE = "StockWatch"
    BINDINGS: ClassVar[list[BindingType]] = [Binding("q", "quit", "Sair")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
