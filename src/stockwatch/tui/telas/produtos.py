"""Tela de produtos: cadastro, edição, exclusão e listagem (REQ-001, 002, 011, 013)."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, Header, Static

from stockwatch.aplicacao.dtos import ResumoProduto
from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto, Modo, TabelaVim, TelaModal
from stockwatch.tui.telas.confirmacao import Confirmacao


class TelaProdutos(TelaModal):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("d", "excluir", "Excluir")]
    DEFAULT_CSS = """
    TelaProdutos #formulario { height: auto; padding: 1 1 0 1; }
    TelaProdutos #formulario Input { width: 1fr; }
    TelaProdutos #vazio { width: 1fr; height: 1fr; content-align: center middle; }
    TelaProdutos DataTable { height: 1fr; margin: 0 1; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self._produtos: dict[str, ResumoProduto] = {}
        self._editando: ResumoProduto | None = None
        self.sub_title = "Produtos"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="formulario"):
            yield CampoTexto(placeholder="Nome do produto", id="nome")
            yield CampoTexto(placeholder="Categoria (opcional)", id="categoria")
        yield LinhaMensagem()
        yield Static("Nenhum produto. Digite o nome acima e pressione Enter.", id="vazio")
        yield TabelaVim(cursor_type="row")
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns("Nome", "Categoria", "Saldo")
        self._recarregar()
        self.query_one("#nome", CampoTexto).focus()

    def produto_em_foco(self) -> str | None:
        tabela = self.query_one(DataTable)
        if self.focused is not tabela or not tabela.row_count:
            return None
        return self._produto_na_linha(tabela.cursor_row).nome

    def on_data_table_row_selected(self, evento: DataTable.RowSelected) -> None:
        """REQ-011: `Enter` numa linha carrega o produto no formulário."""
        produto = self._produto_na_linha(evento.cursor_row)
        self._editando = produto
        self.query_one("#nome", CampoTexto).value = produto.nome
        self.query_one("#categoria", CampoTexto).value = produto.categoria or ""
        self.query_one(LinhaMensagem).info(f"Editando: {produto.nome}. Enter salva, Esc cancela.")
        self.query_one("#nome", CampoTexto).focus()

    def action_excluir(self) -> None:
        """REQ-013: pede confirmação para excluir o produto destacado."""
        tabela = self.query_one(DataTable)
        if self.focused is not tabela or not tabela.row_count:
            return
        produto = self._produto_na_linha(tabela.cursor_row)

        def ao_responder(confirmado: bool | None) -> None:
            if confirmado:
                self._excluir(produto)

        self.app.push_screen(Confirmacao(f"Excluir “{produto.nome}”?"), ao_responder)

    def _excluir(self, produto: ResumoProduto) -> None:
        try:
            nome = self._servico.excluir_produto(produto.id)
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
            return
        self._recarregar()
        self.query_one(LinhaMensagem).sucesso(f"Produto “{nome}” excluído.")

    def action_escape(self) -> None:
        if self.modo is Modo.NORMAL and self._editando is not None:
            self._limpar_formulario()
            self.query_one(LinhaMensagem).info("Edição cancelada.")
            return
        super().action_escape()

    def on_input_submitted(self) -> None:
        nome = self.query_one("#nome", CampoTexto).value
        categoria = self.query_one("#categoria", CampoTexto).value
        try:
            if self._editando is None:
                produto = self._servico.cadastrar_produto(nome, categoria)
                resultado = f"Produto “{produto.nome}” cadastrado."
            else:
                produto = self._servico.editar_produto(self._editando.id, nome, categoria)
                resultado = f"Produto “{produto.nome}” atualizado."
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
            self.query_one("#nome", CampoTexto).focus()
            return
        self._limpar_formulario()
        self._recarregar()
        self.query_one(LinhaMensagem).sucesso(resultado)

    def _limpar_formulario(self) -> None:
        self._editando = None
        for campo in self.query(CampoTexto):
            campo.clear()
        self.modo = Modo.NORMAL
        self.query_one("#nome", CampoTexto).focus()

    def _produto_na_linha(self, linha: int) -> ResumoProduto:
        chave = self.query_one(DataTable).coordinate_to_cell_key(Coordinate(linha, 0)).row_key.value
        assert chave is not None
        return self._produtos[chave]

    def _recarregar(self) -> None:
        produtos = self._servico.listar_produtos()
        self._produtos = {str(p.id): p for p in produtos}
        tabela = self.query_one(DataTable)
        tabela.clear()
        for p in produtos:
            tabela.add_row(p.nome, p.categoria or "—", str(p.saldo), key=str(p.id))
        tabela.display = bool(produtos)
        self.query_one("#vazio").display = not produtos
