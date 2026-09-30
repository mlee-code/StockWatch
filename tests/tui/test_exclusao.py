"""SUITE-TUI: exclusão de produto com confirmação (REQ-013, DECISION-010)."""

from datetime import date

import pytest
from textual.widgets import DataTable

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.confirmacao import Confirmacao
from stockwatch.tui.telas.produtos import TelaProdutos


def _mensagem(app: StockWatchApp) -> str:
    return str(app.screen.query_one("#mensagem").render())


async def test_d_pede_confirmacao_e_s_exclui(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-060: `d` na linha pede confirmação; `s` exclui (REQ-013 CA-1)."""
    servico.cadastrar_produto("Arroz")
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "j", "d")
        assert isinstance(app.screen, Confirmacao)
        assert "Leite" in str(app.screen.query_one("#pergunta").render())
        await piloto.press("s")
        assert isinstance(app.screen, TelaProdutos)
        assert "excluído" in _mensagem(app)
        assert app.screen.query_one(DataTable).row_count == 1
    assert [p.nome for p in servico.listar_produtos()] == ["Arroz"]


@pytest.mark.parametrize("tecla", ["n", "escape"])
async def test_cancelar_nao_exclui(app: StockWatchApp, servico: ServicoEstoque, tecla: str) -> None:
    """TEST-TUI-061: `n` ou `Esc` cancelam sem alterar nada (REQ-013 CA-3)."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "d", tecla)
        assert isinstance(app.screen, TelaProdutos)
    assert [p.nome for p in servico.listar_produtos()] == ["Leite"]


async def test_produto_com_movimentacoes_mostra_motivo(
    app: StockWatchApp, servico: ServicoEstoque
) -> None:
    """TEST-TUI-062: a recusa explica que o histórico seria perdido (REQ-013 CA-2)."""
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 1, date(2099, 1, 1))
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "d", "s")
        assert "histórico" in _mensagem(app)
        assert app.screen.query_one("#mensagem").has_class("erro")


async def test_d_fora_da_tabela_nao_faz_nada(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-063: sem linha em foco, não há o que excluir."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        await piloto.press("p", "d")
        assert isinstance(app.screen, TelaProdutos)
    assert len(servico.listar_produtos()) == 1
