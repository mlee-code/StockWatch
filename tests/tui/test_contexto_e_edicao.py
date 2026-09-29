"""SUITE-TUI: edição de produto e atalhos com contexto (REQ-011, REQ-012, DECISION-009)."""

from datetime import date

from textual.widgets import DataTable, Input

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.entrada import TelaEntrada
from stockwatch.tui.telas.produtos import TelaProdutos


def _valor(app: StockWatchApp, campo: str) -> str:
    return app.screen.query_one(f"#{campo}", Input).value


def _mensagem(app: StockWatchApp) -> str:
    return str(app.screen.query_one("#mensagem").render())


async def test_enter_na_tabela_carrega_produto_para_edicao(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-040: `Enter` numa linha preenche o formulário e avisa que está editando."""
    servico.cadastrar_produto("Arroz", "Grãos")
    servico.cadastrar_produto("Leite", "Laticínios")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "j", "enter")
        assert (_valor(app, "nome"), _valor(app, "categoria")) == ("Leite", "Laticínios")
        assert "Editando: Leite" in _mensagem(app)
        assert app.focused is app.screen.query_one("#nome")


async def test_salva_edicao(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-041: `Enter` no formulário salva a edição e atualiza a tabela (REQ-011)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "enter", "i", "end", *" integral", "enter")
        tabela = app.screen.query_one(DataTable)
        assert str(tabela.get_row_at(0)[0]) == "Leite integral"
        assert "atualizado" in _mensagem(app)
        assert _valor(app, "nome") == ""
    assert [p.nome for p in servico.listar_produtos()] == ["Leite integral"]


async def test_esc_cancela_edicao_sem_sair_da_tela(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-042: `Esc` no modo normal cancela a edição antes de voltar (REQ-011 CA-4)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "enter", "escape")
        assert isinstance(app.screen, TelaProdutos)
        assert _valor(app, "nome") == ""
        await piloto.press("i", *"Arroz", "enter")
    assert [p.nome for p in servico.listar_produtos()] == ["Arroz", "Leite"]


async def test_e_na_tabela_de_produtos_abre_entrada_preenchida(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-043: `e` leva o produto destacado e foca a quantidade (REQ-012 CA-1)."""
    servico.cadastrar_produto("Arroz")
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "j", "e")
        assert isinstance(app.screen, TelaEntrada)
        assert _valor(app, "produto") == "Leite"
        assert app.focused is app.screen.query_one("#quantidade")


async def test_e_no_estoque_abre_entrada_preenchida(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-044: vale também na tela de estoque (REQ-012 CA-1)."""
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
        servico.registrar_entrada(nome, 1, date(2027, 1, 1))
    async with app.run_test() as piloto:
        await piloto.press("t", "j", "e", "i", *"3", "enter")
        assert isinstance(app.screen, TelaEntrada)
    assert servico.estoque_atual()[1].saldo == 4


async def test_sem_tabela_em_foco_entrada_abre_vazia(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-045: com o foco no formulário, `e` abre a entrada vazia (REQ-012 CA-2)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "e")
        assert _valor(app, "produto") == ""
        assert app.focused is app.screen.query_one("#produto")
