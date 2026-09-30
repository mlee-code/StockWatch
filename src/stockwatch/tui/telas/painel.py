"""Painel inicial: resumo do estoque, alertas e atalhos (REQ-009)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from stockwatch.aplicacao.servico import ServicoEstoque

ATALHOS = (
    "p produtos  ·  e entrada  ·  s saída  ·  t estoque  ·  "
    "v validades  ·  c configuração  ·  q sair"
)


class TelaPainel(Screen[None]):
    DEFAULT_CSS = """
    TelaPainel #conteudo { width: 1fr; height: 1fr; align: center middle; }
    TelaPainel #resumo {
        width: auto; padding: 1 4; border: round $panel-lighten-2;
    }
    TelaPainel #atalhos { width: auto; margin-top: 1; color: $text-muted; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="conteudo"):
            yield Static(id="resumo")
            yield Static(ATALHOS, id="atalhos")
        yield Footer()

    def on_mount(self) -> None:
        self.atualizar()

    def on_screen_resume(self) -> None:
        self.atualizar()

    def atualizar(self) -> None:
        painel = self._servico.painel()
        self.query_one("#resumo", Static).update(
            f"Produtos: {painel.produtos}\n"
            f"Unidades: {painel.unidades}\n"
            f"Vencidos: {painel.lotes_vencidos}\n"
            f"Perto de vencer: {painel.lotes_perto} (próximos {painel.dias_alerta} dias)"
        )
