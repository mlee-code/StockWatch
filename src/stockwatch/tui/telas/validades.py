"""Tela de validades: lotes vencidos e perto de vencer (REQ-006)."""

from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from stockwatch.aplicacao.dtos import AlertaValidade
from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.validade import Situacao
from stockwatch.tui.formatos import data_br, descrever_prazo
from stockwatch.tui.modal import TabelaVim, TelaModal


class TelaValidades(TelaModal):
    DEFAULT_CSS = """
    TelaValidades #vazio { width: 1fr; height: 1fr; content-align: center middle; }
    TelaValidades DataTable { height: 1fr; margin: 1 1 0 1; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self._alertas: list[AlertaValidade] = []
        self.sub_title = "Validades"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="vazio")
        yield TabelaVim(cursor_type="row")
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        dias = self._servico.dias_alerta()
        self._alertas = self._servico.validades()
        tabela = self.query_one(DataTable)
        tabela.add_columns("Situação", "Produto", "Validade", "Saldo")
        tema = self.app.current_theme
        cores = {Situacao.VENCIDO: tema.error, Situacao.PERTO: tema.warning}
        for alerta in self._alertas:
            tabela.add_row(
                Text(descrever_prazo(alerta.dias), style=f"bold {cores[alerta.situacao]}"),
                alerta.produto,
                data_br(alerta.validade),
                str(alerta.saldo),
            )
        vazio = self.query_one("#vazio", Static)
        vazio.update(
            f"Nenhum lote vencido ou vencendo nos próximos {dias} dias. "
            "Pressione c para mudar a antecedência."
        )
        vazio.display = not self._alertas
        tabela.display = bool(self._alertas)
        tabela.focus()

    def produto_em_foco(self) -> str | None:
        tabela = self.query_one(DataTable)
        if self.focused is not tabela or not self._alertas:
            return None
        return self._alertas[tabela.cursor_row].produto
