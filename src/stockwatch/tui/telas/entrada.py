"""Tela de registro de entrada (REQ-003)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Header, Label

from stockwatch.aplicacao.dtos import ResumoEntrada
from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import ler_data_opcional, ler_quantidade
from stockwatch.tui.formatos import validade_br
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto
from stockwatch.tui.telas.movimentacao import TelaMovimentacao


def descrever_entrada(resumo: ResumoEntrada) -> str:
    validade = f"validade {validade_br(resumo.validade)}" if resumo.validade else "sem validade"
    return (
        f"Entrada de {resumo.quantidade} un. de {resumo.produto} "
        f"({validade}). Saldo: {resumo.saldo}."
    )


class TelaEntrada(TelaMovimentacao):
    def __init__(self, servico: ServicoEstoque, produto: str | None = None) -> None:
        super().__init__(servico, produto)
        self.sub_title = "Registrar entrada"

    def compose(self) -> ComposeResult:
        nomes = self._nomes_dos_produtos()
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

    def on_input_submitted(self) -> None:
        valor = self._valores()
        try:
            resumo = self._servico.registrar_entrada(
                valor["produto"],
                ler_quantidade(valor["quantidade"]),
                ler_data_opcional(valor["validade"]),
                valor["fornecedor"],
            )
        except ErroDominio as erro:
            self._falhou(str(erro))
        else:
            self._concluiu(descrever_entrada(resumo))
