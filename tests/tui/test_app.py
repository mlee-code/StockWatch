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


async def test_app_usa_tema_neutro_em_tons_de_cinza() -> None:
    """TEST-TUI-002: o tema padrão é neutro, sem cor dominante (UX_UI.md, "Tema")."""
    app = StockWatchApp()
    async with app.run_test():
        assert app.theme == "stockwatch-neutro"
        primaria = app.current_theme.primary
        r, g, b = (int(primaria[i : i + 2], 16) for i in (1, 3, 5))
        assert max(r, g, b) - min(r, g, b) <= 16
