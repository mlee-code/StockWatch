"""Tela de produtos: cadastro e listagem (REQ-001, REQ-002)."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.tui.mensagem import LinhaMensagem


class TelaProdutos(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("escape", "app.pop_screen", "Voltar")]
    DEFAULT_CSS = """
    TelaProdutos #formulario { height: auto; padding: 1 1 0 1; }
    TelaProdutos #formulario Input { width: 1fr; }
    TelaProdutos #vazio { width: 1fr; height: 1fr; content-align: center middle; }
    TelaProdutos DataTable { height: 1fr; margin: 0 1; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self.sub_title = "Produtos"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="formulario"):
            yield Input(placeholder="Nome do produto", id="nome")
            yield Input(placeholder="Categoria (opcional)", id="categoria")
        yield LinhaMensagem()
        yield Static("Nenhum produto. Digite o nome acima e pressione Enter.", id="vazio")
        yield DataTable(cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns("Nome", "Categoria", "Saldo")
        self._recarregar()
        self.query_one("#nome", Input).focus()

    def on_input_submitted(self) -> None:
        nome = self.query_one("#nome", Input)
        categoria = self.query_one("#categoria", Input)
        try:
            produto = self._servico.cadastrar_produto(nome.value, categoria.value)
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
        else:
            self.query_one(LinhaMensagem).sucesso(f"Produto “{produto.nome}” cadastrado.")
            nome.clear()
            categoria.clear()
            self._recarregar()
        nome.focus()

    def _recarregar(self) -> None:
        produtos = self._servico.listar_produtos()
        tabela = self.query_one(DataTable)
        tabela.clear()
        for p in produtos:
            tabela.add_row(p.nome, p.categoria or "—", str(p.saldo), key=str(p.id))
        tabela.display = bool(produtos)
        self.query_one("#vazio").display = not produtos
