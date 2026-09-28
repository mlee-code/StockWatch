"""TEST-TUI-001: a aplicação abre e se identifica."""

from stockwatch.tui.app import StockWatchApp


async def test_app_abre_com_titulo_stockwatch() -> None:
    app = StockWatchApp()
    async with app.run_test():
        assert app.title == "StockWatch"


async def test_app_fecha_com_q() -> None:
    app = StockWatchApp()
    async with app.run_test() as piloto:
        await piloto.press("q")
    assert app.return_code == 0
