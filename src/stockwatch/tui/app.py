"""Aplicação Textual do StockWatch."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header

from stockwatch.tui.tema import TEMA_NEUTRO


class StockWatchApp(App[None]):
    """Ponto de entrada da TUI."""

    TITLE = "StockWatch"
    BINDINGS: ClassVar[list[BindingType]] = [Binding("q", "quit", "Sair")]

    def on_mount(self) -> None:
        self.register_theme(TEMA_NEUTRO)
        self.theme = TEMA_NEUTRO.name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
