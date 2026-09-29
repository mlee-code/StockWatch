"""SUITE-INT: fluxo completo TUI → serviço → SQLite real (TESTS.md, nível 6)."""

from pathlib import Path

from textual.widgets import DataTable

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.sqlite import BancoSqlite
from stockwatch.tui.app import StockWatchApp


async def test_produto_cadastrado_pela_tui_sobrevive_ao_reinicio(caminho_banco: Path) -> None:
    """TEST-INT-011: cadastro pela TUI persiste e reaparece ao reabrir (REQ-001, REQ-010)."""
    banco = BancoSqlite(caminho_banco)
    app = StockWatchApp(ServicoEstoque(banco.nova_unidade))
    async with app.run_test() as piloto:
        await piloto.press("p", "i", *"Arroz", "tab", *"Grãos", "enter")
    banco.fechar()

    reaberto = BancoSqlite(caminho_banco)
    app = StockWatchApp(ServicoEstoque(reaberto.nova_unidade))
    async with app.run_test() as piloto:
        await piloto.press("p")
        tabela = app.screen.query_one(DataTable)
        assert [str(c) for c in tabela.get_row_at(0)] == ["Arroz", "Grãos", "0"]
    reaberto.fechar()
