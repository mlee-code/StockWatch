"""Aplicação Textual do StockWatch."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.modal import TelaModal
from stockwatch.tui.telas.entrada import TelaEntrada
from stockwatch.tui.telas.estoque import TelaEstoque
from stockwatch.tui.telas.produtos import TelaProdutos
from stockwatch.tui.telas.saida import TelaSaida
from stockwatch.tui.tema import TEMA_NEUTRO


class StockWatchApp(App[None]):
    """Ponto de entrada da TUI; recebe o serviço já montado (raiz de composição)."""

    TITLE = "StockWatch"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("p", "produtos", "Produtos"),
        Binding("e", "entrada", "Entrada"),
        Binding("s", "saida", "Saída"),
        Binding("t", "estoque", "Estoque"),
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
        yield Static(
            "p produtos  ·  e entrada  ·  s saída  ·  t estoque  ·  q sair", id="boas-vindas"
        )
        yield Footer()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        # `q` só encerra a partir do painel inicial (UX_UI.md, "Modos").
        if action == "quit" and len(self.screen_stack) > 1:
            return False
        return super().check_action(action, parameters)

    def _abrir(self, tela: Screen[None]) -> None:
        """Troca de tela sem empilhar: volta ao painel e abre a nova."""
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.push_screen(tela)

    def action_produtos(self) -> None:
        self._abrir(TelaProdutos(self.servico))

    def action_entrada(self) -> None:
        """REQ-012: leva o produto em foco, se houver."""
        self._abrir(TelaEntrada(self.servico, self._produto_em_foco()))

    def action_saida(self) -> None:
        """REQ-004, REQ-012: leva o produto em foco, se houver."""
        self._abrir(TelaSaida(self.servico, self._produto_em_foco()))

    def _produto_em_foco(self) -> str | None:
        tela = self.screen
        return tela.produto_em_foco() if isinstance(tela, TelaModal) else None

    def action_estoque(self) -> None:
        self._abrir(TelaEstoque(self.servico))
