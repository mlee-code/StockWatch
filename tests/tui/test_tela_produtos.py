"""SUITE-TUI: tela de produtos (REQ-001, REQ-002, NFR-001, NFR-002)."""

from textual.widgets import DataTable, Static

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.produtos import TelaProdutos


def _mensagem(app: StockWatchApp) -> Static:
    return app.screen.query_one("#mensagem", Static)


async def test_p_abre_produtos_com_estado_vazio(app: StockWatchApp) -> None:
    """TEST-TUI-003: `p` abre a tela; sem produtos, mostra o estado vazio (REQ-002 CA-2)."""
    async with app.run_test() as piloto:
        await piloto.press("p")
        assert isinstance(app.screen, TelaProdutos)
        assert app.screen.query_one("#vazio").display is True
        assert app.screen.query_one(DataTable).display is False


async def test_cadastra_produto_so_pelo_teclado(app: StockWatchApp) -> None:
    """TEST-TUI-004: nome, Tab, categoria, Enter cadastra e lista (REQ-001, NFR-001)."""
    async with app.run_test() as piloto:
        await piloto.press("p")
        await piloto.press(*"Leite", "tab", *"Laticínios", "enter")
        tabela = app.screen.query_one(DataTable)
        assert tabela.display is True
        assert tabela.row_count == 1
        assert [str(c) for c in tabela.get_row_at(0)] == ["Leite", "Laticínios", "0"]
        assert "cadastrado" in str(_mensagem(app).render())
        assert _mensagem(app).has_class("sucesso")


async def test_formulario_limpo_e_foco_no_nome_apos_sucesso(app: StockWatchApp) -> None:
    """TEST-TUI-005: após cadastrar, o formulário fica pronto para o próximo (UX_UI)."""
    async with app.run_test() as piloto:
        await piloto.press("p", *"Leite", "enter")
        assert app.focused is not None
        assert app.focused.id == "nome"
        assert app.screen.query_one("#nome").value == ""  # type: ignore[attr-defined]


async def test_duplicado_mostra_erro_e_nao_altera_lista(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-006: erro de validação é mostrado sem traceback (REQ-001 CA-2, NFR-002)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", *"LEITE", "enter")
        assert "Já existe" in str(_mensagem(app).render())
        assert _mensagem(app).has_class("erro")
        assert app.screen.query_one(DataTable).row_count == 1


async def test_nome_vazio_mostra_erro(app: StockWatchApp) -> None:
    """TEST-TUI-007: Enter sem nome mostra a regra violada (REQ-001 CA-1, NFR-002)."""
    async with app.run_test() as piloto:
        await piloto.press("p", "enter")
        assert "obrigatório" in str(_mensagem(app).render())


async def test_esc_volta_para_o_inicio(app: StockWatchApp) -> None:
    """TEST-TUI-008: Esc volta à tela inicial (UX_UI, "Mapa de telas")."""
    async with app.run_test() as piloto:
        await piloto.press("p", "escape")
        assert not isinstance(app.screen, TelaProdutos)
