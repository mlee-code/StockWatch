"""Tela de histórico de movimentações, somente leitura (REQ-008)."""

from textual.app import ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import TipoMovimentacao
from stockwatch.tui.formatos import instante_local
from stockwatch.tui.modal import TabelaVim, TelaModal

LIMITE = 500


class TelaHistorico(TelaModal):
    DEFAULT_CSS = """
    TelaHistorico #vazio { width: 1fr; height: 1fr; content-align: center middle; }
    TelaHistorico DataTable { height: 1fr; margin: 1 1 0 1; }
    """

    def __init__(self, servico: ServicoEstoque, produto: str | None = None) -> None:
        super().__init__()
        self._servico = servico
        self._produto = produto
        self.sub_title = f"Histórico: {produto}" if produto else "Histórico"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Nenhuma movimentação registrada.", id="vazio")
        yield TabelaVim(cursor_type="row")
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        produto_id = next(
            (p.id for p in self._servico.listar_produtos() if p.nome == self._produto), None
        )
        itens = self._servico.historico(limite=LIMITE, produto_id=produto_id)
        tabela = self.query_one(DataTable)
        tabela.add_columns("Data e hora", "Tipo", "Motivo", "Produto", "Quantidade")
        for item in itens:
            tabela.add_row(
                instante_local(item.ocorrida_em),
                "Entrada" if item.tipo is TipoMovimentacao.ENTRADA else "Saída",
                item.motivo.rotulo if item.motivo else "—",
                item.produto,
                str(item.quantidade),
            )
        self.query_one("#vazio").display = not itens
        tabela.display = bool(itens)
        tabela.focus()
