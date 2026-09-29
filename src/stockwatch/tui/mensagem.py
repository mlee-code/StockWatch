"""Linha de resultado das ações: sucesso em verde, erro em vermelho (UX_UI.md, "Estados")."""

from textual.widgets import Static


class LinhaMensagem(Static):
    DEFAULT_CSS = """
    LinhaMensagem { height: auto; padding: 0 2; }
    LinhaMensagem.sucesso { color: $success; }
    LinhaMensagem.erro { color: $error; }
    """

    def __init__(self) -> None:
        super().__init__("", id="mensagem")

    def sucesso(self, texto: str) -> None:
        self._mostrar(texto, sucesso=True)

    def erro(self, texto: str) -> None:
        self._mostrar(texto, sucesso=False)

    def _mostrar(self, texto: str, *, sucesso: bool) -> None:
        self.update(texto)
        self.set_class(sucesso, "sucesso")
        self.set_class(not sucesso, "erro")
