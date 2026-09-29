"""Pergunta sim/não sobre uma ação destrutiva (REQ-013 CA-3)."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class Confirmacao(ModalScreen[bool]):
    """Devolve True com `s`/`y`; False com `n`/`Esc`."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("s,y", "responder(True)", "Sim"),
        Binding("n,escape", "responder(False)", "Não"),
    ]
    DEFAULT_CSS = """
    Confirmacao { align: center middle; }
    Confirmacao #caixa {
        width: 60; height: auto; padding: 1 2;
        border: round $warning; background: $surface;
    }
    Confirmacao #opcoes { color: $text-muted; margin-top: 1; }
    """

    def __init__(self, pergunta: str) -> None:
        super().__init__()
        self._pergunta = pergunta

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa"):
            yield Static(self._pergunta, id="pergunta")
            yield Static("s: sim    n / Esc: não", id="opcoes")

    def action_responder(self, resposta: bool) -> None:
        self.dismiss(resposta)
