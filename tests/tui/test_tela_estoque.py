"""SUITE-TUI: estoque atual e lotes (REQ-005, NFR-002)."""

from datetime import date

from textual.widgets import DataTable

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.estoque import TelaEstoque


def _linhas(tabela: DataTable[str]) -> list[list[str]]:
    return [[str(c) for c in tabela.get_row_at(i)] for i in range(tabela.row_count)]


async def test_estoque_vazio(app: StockWatchApp) -> None:
    """TEST-TUI-020: sem saldo, estado vazio que explica a próxima ação (NFR-002)."""
    async with app.run_test() as piloto:
        await piloto.press("t")
        assert isinstance(app.screen, TelaEstoque)
        assert app.screen.query_one("#vazio").display is True
        assert app.screen.query_one("#estoque").display is False


async def test_estoque_e_lotes_do_produto_selecionado(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-021: produtos com saldo e lotes do produto destacado (REQ-005 CA-1, CA-2)."""
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Arroz", 3, date(2027, 1, 1))
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1), "Sul")
    servico.registrar_entrada("Leite", 2, date(2026, 10, 3))
    async with app.run_test() as piloto:
        await piloto.press("t")
        estoque = app.screen.query_one("#estoque", DataTable)
        lotes = app.screen.query_one("#lotes", DataTable)
        assert _linhas(estoque) == [["Arroz", "3", "01/01/2027"], ["Leite", "7", "03/10/2026"]]
        assert _linhas(lotes) == [["01/01/2027", "—", "3"]]
        await piloto.press("down")
        assert _linhas(lotes) == [["03/10/2026", "—", "2"], ["01/11/2026", "Sul", "5"]]


async def test_esc_volta_ao_inicio(app: StockWatchApp) -> None:
    """TEST-TUI-022: Esc volta à tela inicial."""
    async with app.run_test() as piloto:
        await piloto.press("t", "escape")
        assert not isinstance(app.screen, TelaEstoque)


async def test_estoque_mostra_sem_validade(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-023: produto só com lotes sem data aparece "sem validade" (REQ-005 CA-1)."""
    servico.cadastrar_produto("Vassoura")
    servico.registrar_entrada("Vassoura", 2, None)
    async with app.run_test() as piloto:
        await piloto.press("t")
        estoque = app.screen.query_one("#estoque", DataTable)
        lotes = app.screen.query_one("#lotes", DataTable)
        assert _linhas(estoque) == [["Vassoura", "2", "sem validade"]]
        assert _linhas(lotes) == [["sem validade", "—", "2"]]
