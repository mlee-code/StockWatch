"""Base das telas de entrada e de saída: produto em foco e ciclo do formulário."""

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.mensagem import LinhaMensagem
from stockwatch.tui.modal import CampoTexto, Modo, TelaModal


class TelaMovimentacao(TelaModal):
    DEFAULT_CSS = """
    TelaMovimentacao #formulario { height: auto; width: 60; padding: 1 2; }
    TelaMovimentacao Label { margin-top: 1; }
    """

    def __init__(self, servico: ServicoEstoque, produto: str | None = None) -> None:
        super().__init__()
        self._servico = servico
        self._produto_inicial = produto

    def _nomes_dos_produtos(self) -> list[str]:
        return [p.nome for p in self._servico.listar_produtos()]

    def on_mount(self) -> None:
        """REQ-012: com produto em foco na tela anterior, começa pela quantidade."""
        if self._produto_inicial:
            self.query_one("#produto", CampoTexto).value = self._produto_inicial
            self.query_one("#quantidade", CampoTexto).focus()
        else:
            self.query_one("#produto", CampoTexto).focus()

    def _valores(self) -> dict[str | None, str]:
        return {campo.id: campo.value for campo in self.query(CampoTexto)}

    def _falhou(self, texto: str) -> None:
        self.query_one(LinhaMensagem).erro(texto)
        self.query_one("#produto", CampoTexto).focus()

    def _concluiu(self, texto: str) -> None:
        self.query_one(LinhaMensagem).sucesso(texto)
        for campo in self.query(CampoTexto):
            campo.clear()
        self.modo = Modo.NORMAL
        self.query_one("#produto", CampoTexto).focus()
