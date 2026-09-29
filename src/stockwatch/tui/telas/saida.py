"""Tela de registro de saída (REQ-004)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Header, Label

from stockwatch.aplicacao.dtos import ResumoSaida
from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import ler_motivo, ler_quantidade
from stockwatch.tui.formatos import validade_br
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto, Modo, TelaModal


def descrever_saida(resumo: ResumoSaida) -> str:
    lotes = ", ".join(
        f"{quantidade} do lote {validade_br(validade)}" for validade, quantidade in resumo.consumos
    )
    return (
        f"{resumo.motivo.rotulo} de {resumo.quantidade} un. de {resumo.produto}: "
        f"{lotes}. Saldo: {resumo.saldo}."
    )


class TelaSaida(TelaModal):
    DEFAULT_CSS = """
    TelaSaida #formulario { height: auto; width: 60; padding: 1 2; }
    TelaSaida Label { margin-top: 1; }
    """

    def __init__(self, servico: ServicoEstoque, produto: str | None = None) -> None:
        super().__init__()
        self._servico = servico
        self._produto_inicial = produto
        self.sub_title = "Registrar saída"

    def compose(self) -> ComposeResult:
        nomes = [p.nome for p in self._servico.listar_produtos()]
        motivos = ["venda", "perda", "descarte por vencimento"]
        yield Header()
        with Vertical(id="formulario"):
            yield Label("Produto (→ completa o nome)")
            yield CampoTexto(id="produto", suggester=SuggestFromList(nomes, case_sensitive=False))
            yield Label("Quantidade")
            yield CampoTexto(id="quantidade", placeholder="unidades inteiras")
            yield Label("Motivo: (v)enda, (p)erda, (d)escarte por vencimento; em branco, venda")
            yield CampoTexto(id="motivo", suggester=SuggestFromList(motivos, case_sensitive=False))
        yield LinhaMensagem()
        yield self.indicador_de_modo()
        yield Footer()

    def on_mount(self) -> None:
        if self._produto_inicial:
            self.query_one("#produto", CampoTexto).value = self._produto_inicial
            self.query_one("#quantidade", CampoTexto).focus()
        else:
            self.query_one("#produto", CampoTexto).focus()

    def on_input_submitted(self) -> None:
        valor = {campo.id: campo.value for campo in self.query(CampoTexto)}
        try:
            resumo = self._servico.registrar_saida(
                valor["produto"], ler_quantidade(valor["quantidade"]), ler_motivo(valor["motivo"])
            )
        except ErroDominio as erro:
            self.query_one(LinhaMensagem).erro(str(erro))
        else:
            self.query_one(LinhaMensagem).sucesso(descrever_saida(resumo))
            for campo in self.query(CampoTexto):
                campo.clear()
            self.modo = Modo.NORMAL
        self.query_one("#produto", CampoTexto).focus()
