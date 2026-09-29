"""Tela de registro de entrada (REQ-003)."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.screen import Screen
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Header, Input, Label

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import ler_data, ler_quantidade
from stockwatch.tui.formatos import data_br
from stockwatch.tui.mensagem import LinhaMensagem


class TelaEntrada(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("escape", "app.pop_screen", "Voltar")]
    DEFAULT_CSS = """
    TelaEntrada #formulario { height: auto; width: 60; padding: 1 2; }
    TelaEntrada Label { margin-top: 1; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self.sub_title = "Registrar entrada"

    def compose(self) -> ComposeResult:
        nomes = [p.nome for p in self._servico.listar_produtos()]
        yield Header()
        with Vertical(id="formulario"):
            yield Label("Produto (→ completa o nome)")
            yield Input(id="produto", suggester=SuggestFromList(nomes, case_sensitive=False))
            yield Label("Quantidade")
            yield Input(id="quantidade", placeholder="unidades inteiras")
            yield Label("Validade")
            yield Input(id="validade", placeholder="DD/MM/AAAA")
            yield Label("Fornecedor (opcional)")
            yield Input(id="fornecedor")
        yield LinhaMensagem()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#produto", Input).focus()

    def on_input_submitted(self) -> None:
        valor = {campo.id: campo.value for campo in self.query(Input)}
        try:
            resumo = self._servico.registrar_entrada(
                valor["produto"],
                ler_quantidade(valor["quantidade"]),
                ler_data(valor["validade"]),
                valor["fornecedor"],
            )
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
        else:
            self.query_one(LinhaMensagem).sucesso(
                f"Entrada de {resumo.quantidade} un. de {resumo.produto} "
                f"(validade {data_br(resumo.validade)}). Saldo: {resumo.saldo}."
            )
            for campo in self.query(Input):
                campo.clear()
        self.query_one("#produto", Input).focus()
