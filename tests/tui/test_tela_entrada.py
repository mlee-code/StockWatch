"""SUITE-TUI: registro de entrada (REQ-003, NFR-001, NFR-002)."""

from datetime import date

from textual.widgets import Input, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.entrada import TelaEntrada


def _mensagem(app: StockWatchApp) -> str:
    return str(app.screen.query_one("#mensagem", Static).render())


async def test_registra_entrada_so_pelo_teclado(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-010: produto, quantidade, validade e fornecedor; Enter registra (REQ-003)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("e")
        assert isinstance(app.screen, TelaEntrada)
        await piloto.press(*"Leite", "tab", *"12", "tab", *"10/10/2026", "tab", *"Sul", "enter")
        assert "Saldo: 12" in _mensagem(app)
        assert app.screen.query_one("#mensagem").has_class("sucesso")
    [item] = servico.estoque_atual()
    assert (item.saldo, item.proxima_validade) == (12, date(2026, 10, 10))


async def test_formulario_limpo_e_foco_no_produto(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-011: após sucesso, pronto para a próxima entrada (UX_UI)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("e", *"Leite", "tab", "1", "tab", *"2026-10-10", "enter")
        assert app.focused is not None
        assert app.focused.id == "produto"
        assert all(campo.value == "" for campo in app.screen.query(Input))


async def test_quantidade_invalida_mostra_erro_e_nao_grava(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-012: quantidade inválida é explicada ao operador (REQ-003 CA-1, NFR-002)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("e", *"Leite", "tab", "0", "tab", *"10/10/2026", "enter")
        assert "inteiro maior que zero" in _mensagem(app)
        assert app.screen.query_one("#mensagem").has_class("erro")
    assert servico.estoque_atual() == []


async def test_validade_invalida_mostra_erro(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-013: validade obrigatória e válida (REQ-003 CA-2)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("e", *"Leite", "tab", "1", "enter")
        assert "DD/MM/AAAA" in _mensagem(app)


async def test_produto_desconhecido_mostra_erro(app: StockWatchApp) -> None:
    """TEST-TUI-014: entrada só para produto cadastrado (REQ-003)."""
    async with app.run_test() as piloto:
        await piloto.press("e", *"Feijão", "tab", "1", "tab", *"10/10/2026", "enter")
        assert "Não há produto" in _mensagem(app)


async def test_nome_do_produto_e_sugerido(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-015: digitar o início e → completa o nome cadastrado (NFR-001)."""
    servico.cadastrar_produto("Leite integral")
    async with app.run_test() as piloto:
        await piloto.press("e", *"lei", "right")
        assert app.screen.query_one("#produto", Input).value == "Leite integral"


async def test_esc_volta_ao_inicio(app: StockWatchApp) -> None:
    """TEST-TUI-016: Esc volta à tela inicial."""
    async with app.run_test() as piloto:
        await piloto.press("e", "escape")
        assert not isinstance(app.screen, TelaEntrada)
