"""Tela de configuração: antecedência do alerta de validade (REQ-007)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Label

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import ler_dias_alerta
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto, Modo, TelaModal


class TelaConfiguracao(TelaModal):
    DEFAULT_CSS = """
    TelaConfiguracao #formulario { height: auto; width: 60; padding: 1 2; }
    """

    def __init__(self, servico: ServicoEstoque) -> None:
        super().__init__()
        self._servico = servico
        self.sub_title = "Configuração"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="formulario"):
            yield Label("Alertar validades com quantos dias de antecedência? (0 a 365)")
            yield CampoTexto(str(self._servico.dias_alerta()), id="dias")
        yield LinhaMensagem()
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#dias", CampoTexto).focus()

    def on_input_submitted(self) -> None:
        campo = self.query_one("#dias", CampoTexto)
        try:
            dias = self._servico.configurar_dias_alerta(ler_dias_alerta(campo.value))
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
            return
        self.query_one(LinhaMensagem).sucesso(f"Antecedência do alerta: {dias} dias.")
        campo.value = str(dias)
        self.modo = Modo.NORMAL
