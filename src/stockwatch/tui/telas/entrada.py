"""Tela de registro de entrada (REQ-003)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Header, Label

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import ler_data_opcional, ler_quantidade
from stockwatch.tui.formatos import validade_br
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto, Modo, TelaModal


class TelaEntrada(TelaModal):
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
            yield CampoTexto(id="produto", suggester=SuggestFromList(nomes, case_sensitive=False))
            yield Label("Quantidade")
            yield CampoTexto(id="quantidade", placeholder="unidades inteiras")
            yield Label("Validade (em branco: não vence)")
            yield CampoTexto(id="validade", placeholder="DD/MM/AAAA")
            yield Label("Fornecedor (opcional)")
            yield CampoTexto(id="fornecedor")
        yield LinhaMensagem()
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#produto", CampoTexto).focus()

    def on_input_submitted(self) -> None:
        valor = {campo.id: campo.value for campo in self.query(CampoTexto)}
        try:
            resumo = self._servico.registrar_entrada(
                valor["produto"],
                ler_quantidade(valor["quantidade"]),
                ler_data_opcional(valor["validade"]),
                valor["fornecedor"],
            )
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
        else:
            validade = validade_br(resumo.validade)
            if resumo.validade:
                validade = f"validade {validade}"
            self.query_one(LinhaMensagem).sucesso(
                f"Entrada de {resumo.quantidade} un. de {resumo.produto} "
                f"({validade}). Saldo: {resumo.saldo}."
            )
            for campo in self.query(CampoTexto):
                campo.clear()
            self.modo = Modo.NORMAL
        self.query_one("#produto", CampoTexto).focus()
