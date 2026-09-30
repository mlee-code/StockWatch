"""Painel inicial: resumo do estoque, alertas e atalhos (REQ-009)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from stockwatch.aplicacao.servico import ServicoEstoque

ATALHOS = (
    "p produtos  ·  e entrada  ·  s saída  ·  t estoque  ·  "
    "v validades  ·  m histórico  ·  c configuração  ·  q sair"
)


class TelaPainel(Screen[None]):
    DEFAULT_CSS = """
    TelaPainel #conteudo { width: 1fr; height: 1fr; align: center middle; padding: 0 2; }
    TelaPainel #resumo {
        width: 1fr; padding: 1 2; text-align: center;
        border: round $panel-lighten-2; border-title-align: center;
    }
    TelaPainel #atalhos { width: 1fr; margin-top: 1; text-align: center; color: $text-muted; }
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
        self.query_one("#resumo", Static).border_title = "Resumo do estoque"
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
