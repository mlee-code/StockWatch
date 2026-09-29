"""SUITE-TUI: registro de saída (REQ-004, REQ-012, NFR-002)."""

from datetime import date

from textual.widgets import Input

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.saida import TelaSaida

LONGE = date(2099, 1, 1)


def _mensagem(app: StockWatchApp) -> str:
    return str(app.screen.query_one("#mensagem").render())


async def test_venda_por_teclado_mostra_lotes_consumidos(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-050: motivo em branco é venda; a mensagem mostra lotes e saldo (REQ-004)."""
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, date(2098, 1, 1))
    servico.registrar_entrada("Leite", 5, LONGE)
    async with app.run_test() as piloto:
        await piloto.press("s")
        assert isinstance(app.screen, TelaSaida)
        await piloto.press("i", *"Leite", "tab", "3", "enter")
        mensagem = _mensagem(app)
        assert "Venda de 3 un. de Leite" in mensagem
        assert "2 do lote 01/01/2098" in mensagem
        assert "1 do lote 01/01/2099" in mensagem
        assert "Saldo: 4" in mensagem
    assert servico.estoque_atual()[0].saldo == 4


async def test_saldo_insuficiente_mostra_erro(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-051: rejeição explicada ao operador (REQ-004 CA-4, NFR-002)."""
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, LONGE)
    async with app.run_test() as piloto:
        await piloto.press("s", "i", *"Leite", "tab", "5", "enter")
        assert "disponível 2" in _mensagem(app)
        assert app.screen.query_one("#mensagem").has_class("erro")
    assert servico.estoque_atual()[0].saldo == 2


async def test_motivo_invalido_mostra_opcoes(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-052: motivo desconhecido lista as opções (REQ-004 CA-1)."""
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, LONGE)
    async with app.run_test() as piloto:
        await piloto.press("s", "i", *"Leite", "tab", "1", "tab", *"roubo", "enter")
        assert "perda" in _mensagem(app)


async def test_perda_pela_inicial(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-053: `p` no campo de motivo registra perda."""
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, LONGE)
    async with app.run_test() as piloto:
        await piloto.press("s", "i", *"Leite", "tab", "1", "tab", "p", "enter")
        assert "Perda de 1 un. de Leite" in _mensagem(app)


async def test_s_no_estoque_abre_saida_preenchida(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-054: `s` leva o produto em foco e foca a quantidade (REQ-012)."""
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
        servico.registrar_entrada(nome, 3, LONGE)
    async with app.run_test() as piloto:
        await piloto.press("t", "j", "s")
        assert isinstance(app.screen, TelaSaida)
        assert app.screen.query_one("#produto", Input).value == "Leite"
        assert app.focused is app.screen.query_one("#quantidade")


async def test_esc_volta_ao_inicio(app: StockWatchApp) -> None:
    """TEST-TUI-055: `Esc` no modo normal volta ao painel."""
    async with app.run_test() as piloto:
        await piloto.press("s", "escape")
        assert not isinstance(app.screen, TelaSaida)
