"""SUITE-TUI: modos normal e inserção (FR-002, DECISION-008, UX_UI.md)."""

from datetime import date

from textual.widgets import DataTable, Input, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.entrada import TelaEntrada
from stockwatch.tui.telas.produtos import TelaProdutos


def _modo(app: StockWatchApp) -> str:
    return str(app.screen.query_one("#modo", Static).render())


def _campo(app: StockWatchApp, campo: str) -> Input:
    return app.screen.query_one(f"#{campo}", Input)


async def test_tela_abre_em_modo_normal_e_letras_nao_digitam(app: StockWatchApp) -> None:
    """TEST-TUI-030: ao abrir, modo NORMAL; letras não alteram o campo."""
    async with app.run_test() as piloto:
        await piloto.press("e")
        assert "NORMAL" in _modo(app)
        await piloto.press("x", "y", "backspace")
        assert _campo(app, "produto").value == ""


async def test_i_entra_em_insercao_e_esc_volta_ao_normal(app: StockWatchApp) -> None:
    """TEST-TUI-031: `i` digita no campo focado; `Esc` volta ao normal sem sair da tela."""
    async with app.run_test() as piloto:
        await piloto.press("e", "i")
        assert "INSERÇÃO" in _modo(app)
        await piloto.press(*"jk", "escape")
        assert _campo(app, "produto").value == "jk"
        assert "NORMAL" in _modo(app)
        assert isinstance(app.screen, TelaEntrada)


async def test_esc_no_normal_volta_ao_painel(app: StockWatchApp) -> None:
    """TEST-TUI-032: `Esc` no modo normal volta à tela inicial."""
    async with app.run_test() as piloto:
        await piloto.press("e", "i", "escape", "escape")
        assert not isinstance(app.screen, TelaEntrada)


async def test_j_k_h_l_movem_entre_campos(app: StockWatchApp) -> None:
    """TEST-TUI-033: `j`/`l` avançam e `k`/`h` recuam entre campos no modo normal."""
    async with app.run_test() as piloto:
        await piloto.press("e", "j", "j")
        assert app.focused is _campo(app, "validade")
        await piloto.press("k")
        assert app.focused is _campo(app, "quantidade")
        await piloto.press("l", "l", "h")
        assert app.focused is _campo(app, "validade")


async def test_i_em_outro_campo_digita_nele(app: StockWatchApp) -> None:
    """TEST-TUI-034: navegar com `j` e inserir no campo escolhido."""
    async with app.run_test() as piloto:
        await piloto.press("e", "j", "i", *"12")
        assert _campo(app, "quantidade").value == "12"


async def test_enter_no_normal_confirma_e_sucesso_volta_ao_normal(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-035: `Enter` confirma; após sucesso, o modo volta a NORMAL."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("e", "i", *"Leite", "tab", "3", "escape", "enter")
        assert servico.estoque_atual()[0].saldo == 3
        await piloto.press("e", "i", *"Leite", "tab", "1", "enter")
        assert "NORMAL" in _modo(app)
        assert servico.estoque_atual()[0].saldo == 4


async def test_j_k_movem_linhas_da_tabela(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-036: numa tabela, `j`/`k` descem e sobem linhas."""
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
        servico.registrar_entrada(nome, 1, date(2027, 1, 1))
    async with app.run_test() as piloto:
        await piloto.press("t", "j")
        assert app.screen.query_one("#estoque", DataTable).cursor_row == 1
        await piloto.press("k")
        assert app.screen.query_one("#estoque", DataTable).cursor_row == 0


async def test_teclas_globais_trocam_de_tela_sem_empilhar(app: StockWatchApp) -> None:
    """TEST-TUI-037: `p` na tela de entrada abre produtos no lugar dela."""
    async with app.run_test() as piloto:
        await piloto.press("e", "p")
        assert isinstance(app.screen, TelaProdutos)
        assert len(app.screen_stack) == 2


async def test_q_so_sai_a_partir_do_painel(app: StockWatchApp) -> None:
    """TEST-TUI-038: em outra tela, `q` não fecha o programa."""
    async with app.run_test() as piloto:
        await piloto.press("e", "q")
        assert isinstance(app.screen, TelaEntrada)
        assert app.is_running
