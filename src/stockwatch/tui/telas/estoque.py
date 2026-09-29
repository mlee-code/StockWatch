"""Tela de estoque atual com os lotes do produto destacado (REQ-005)."""

from textual.app import ComposeResult
from textual.widgets import DataTable, Footer, Header, Label, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.formatos import validade_br
from stockwatch.tui.modal import TabelaVim, TelaModal


class TelaEstoque(TelaModal):
    DEFAULT_CSS = """
    TelaEstoque #vazio { width: 1fr; height: 1fr; content-align: center middle; }
    TelaEstoque #estoque { height: 2fr; margin: 1 1 0 1; }
    TelaEstoque #titulo-lotes { margin: 1 2 0 2; color: $text-muted; }
    TelaEstoque #lotes { height: 1fr; margin: 0 1; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self.sub_title = "Estoque atual"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Nenhum produto em estoque. Pressione Esc e depois e para registrar uma entrada.",
            id="vazio",
        )
        yield TabelaVim(id="estoque", cursor_type="row")
        yield Label("Lotes do produto selecionado", id="titulo-lotes")
        yield TabelaVim(id="lotes", cursor_type="row")
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        estoque = self.query_one("#estoque", DataTable)
        estoque.add_columns("Produto", "Saldo", "Próxima validade")
        self.query_one("#lotes", DataTable).add_columns("Validade", "Fornecedor", "Saldo")
        itens = self._servico.estoque_atual()
        for item in itens:
            estoque.add_row(
                item.produto,
                str(item.saldo),
                validade_br(item.proxima_validade),
                key=str(item.produto_id),
            )
        self.query_one("#vazio").display = not itens
        for widget in self.query("#estoque, #titulo-lotes, #lotes"):
            widget.display = bool(itens)
        estoque.focus()

    def produto_em_foco(self) -> str | None:
        tabela = self.query_one("#estoque", DataTable)
        if self.focused is not tabela or not tabela.row_count:
            return None
        return str(tabela.get_row_at(tabela.cursor_row)[0])

    def on_data_table_row_highlighted(self, evento: DataTable.RowHighlighted) -> None:
        if evento.data_table.id != "estoque" or evento.row_key.value is None:
            return
        lotes = self.query_one("#lotes", DataTable)
        lotes.clear()
        for lote in self._servico.lotes_do_produto(int(evento.row_key.value)):
            lotes.add_row(validade_br(lote.validade), lote.fornecedor or "—", str(lote.saldo))
