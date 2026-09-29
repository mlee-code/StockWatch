"""Aplicação Textual do StockWatch."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Header, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.telas.produtos import TelaProdutos
from stockwatch.tui.tema import TEMA_NEUTRO


class StockWatchApp(App[None]):
    """Ponto de entrada da TUI; recebe o serviço já montado (raiz de composição)."""

    TITLE = "StockWatch"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("p", "produtos", "Produtos"),
        Binding("q", "quit", "Sair"),
    ]
    CSS = "#boas-vindas { width: 1fr; height: 1fr; content-align: center middle; }"

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self.servico = servico

    def on_mount(self) -> None:
        self.register_theme(TEMA_NEUTRO)
        self.theme = TEMA_NEUTRO.name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Pressione p para cadastrar e listar produtos.", id="boas-vindas")
        yield Footer()

    def action_produtos(self) -> None:
        self.push_screen(TelaProdutos(self.servico))
