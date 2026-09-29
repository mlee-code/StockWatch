"""Modos normal e inserção, como no vim (DECISION-008, UX_UI.md)."""

from enum import StrEnum
from typing import ClassVar

from textual import events
from textual.binding import Binding, BindingType
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Input, Static


class Modo(StrEnum):
    NORMAL = "NORMAL"
    INSERCAO = "INSERÇÃO"


class TelaModal(Screen[None]):
    """Tela com modo normal (navegação) e modo inserção (digitação)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "escape", "Voltar / normal"),
        Binding("i", "inserir", "Inserir"),
        Binding("j,l", "app.focus_next", "Próximo", show=False),
        Binding("k,h", "app.focus_previous", "Anterior", show=False),
    ]
    DEFAULT_CSS = """
    TelaModal #modo { dock: bottom; height: 1; padding: 0 1; color: $text-muted; }
    TelaModal #modo.insercao { color: $warning; text-style: bold; }
    """

    modo: reactive[Modo] = reactive(Modo.NORMAL)

    def indicador_de_modo(self) -> Static:
        return Static(f"-- {Modo.NORMAL} --", id="modo")

    def watch_modo(self, modo: Modo) -> None:
        for indicador in self.query("#modo").results(Static):
            indicador.update(f"-- {modo} --")
            indicador.set_class(modo is Modo.INSERCAO, "insercao")

    def action_escape(self) -> None:
        if self.modo is Modo.INSERCAO:
            self.modo = Modo.NORMAL
        else:
            self.app.pop_screen()

    def produto_em_foco(self) -> str | None:
        """Produto destacado numa tabela em foco, para atalhos com contexto (REQ-012)."""
        return None

    def action_inserir(self) -> None:
        if isinstance(self.focused, CampoTexto):
            self.modo = Modo.INSERCAO


class CampoTexto(Input):
    """Input que só aceita edição no modo inserção da tela."""

    _ACOES_DE_EDICAO = ("delete", "cut", "paste", "transpose")

    def _em_insercao(self) -> bool:
        return isinstance(self.screen, TelaModal) and self.screen.modo is Modo.INSERCAO

    def check_consume_key(self, key: str, character: str | None) -> bool:
        # No modo normal, as letras seguem para os atalhos da tela e do app.
        return self._em_insercao() and super().check_consume_key(key, character)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action.startswith(self._ACOES_DE_EDICAO) and not self._em_insercao():
            return False
        return super().check_action(action, parameters)

    async def _on_key(self, event: events.Key) -> None:
        # O Textual chama o _on_key de cada classe da MRO; prevent_default()
        # impede o Input de inserir a tecla, que segue para os atalhos.
        if not self._em_insercao():
            event.prevent_default()


class TabelaVim(DataTable[str]):
    """DataTable navegável com `j`/`k`."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Descer", show=False),
        Binding("k", "cursor_up", "Subir", show=False),
    ]
