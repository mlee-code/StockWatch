"""SUITE-TUI: validades, configuração e painel (REQ-006, 007, 009, NFR-002)."""

from datetime import date

import pytest
from rich.text import Text
from textual.widgets import DataTable, Input

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.configuracao import TelaConfiguracao
from stockwatch.tui.telas.entrada import TelaEntrada
from stockwatch.tui.telas.validades import TelaValidades
from tests.fakes import UnidadeDeTrabalhoEmMemoria

HOJE = date(2026, 10, 1)


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    return ServicoEstoque(lambda: banco, hoje=lambda: HOJE)


@pytest.fixture
def com_estoque(servico: ServicoEstoque) -> ServicoEstoque:
    for nome in ["Arroz", "Leite", "Vassoura"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Leite", 4, date(2026, 9, 28))
    servico.registrar_entrada("Arroz", 2, date(2026, 10, 1))
    servico.registrar_entrada("Leite", 5, date(2026, 10, 11))
    servico.registrar_entrada("Arroz", 7, date(2027, 6, 1))
    servico.registrar_entrada("Vassoura", 3, None)
    return servico


def _linhas(app: StockWatchApp) -> list[list[str]]:
    tabela = app.screen.query_one(DataTable)
    return [[str(c) for c in tabela.get_row_at(i)] for i in range(tabela.row_count)]


def _texto(app: StockWatchApp, seletor: str) -> str:
    return str(app.screen.query_one(seletor).render())


async def test_validades_sem_alertas(app: StockWatchApp) -> None:
    """TEST-TUI-070: estado vazio cita a antecedência (REQ-006, NFR-002)."""
    async with app.run_test() as piloto:
        await piloto.press("v")
        assert isinstance(app.screen, TelaValidades)
        assert "30 dias" in _texto(app, "#vazio")
        assert app.screen.query_one(DataTable).display is False


async def test_validades_listadas_com_situacao_em_texto_e_cor(
    app: StockWatchApp, com_estoque: ServicoEstoque
) -> None:
    """TEST-TUI-071: situação em texto e em cor, do mais urgente (REQ-006 CA-3, UX_UI)."""
    async with app.run_test() as piloto:
        await piloto.press("v")
        assert _linhas(app) == [
            ["vencido há 3 dias", "Leite", "28/09/2026", "4"],
            ["vence hoje", "Arroz", "01/10/2026", "2"],
            ["vence em 10 dias", "Leite", "11/10/2026", "5"],
        ]
        celula = app.screen.query_one(DataTable).get_row_at(0)[0]
        assert isinstance(celula, Text)
        assert celula.style


async def test_e_numa_validade_abre_entrada_do_produto(
    app: StockWatchApp, com_estoque: ServicoEstoque
) -> None:
    """TEST-TUI-072: validades também oferecem o produto em foco (REQ-012)."""
    async with app.run_test() as piloto:
        await piloto.press("v", "j", "e")
        assert isinstance(app.screen, TelaEntrada)
        assert app.screen.query_one("#produto", Input).value == "Arroz"


async def test_configura_antecedencia(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-073: `c` mostra o valor atual e salva o novo (REQ-007)."""
    async with app.run_test() as piloto:
        await piloto.press("c")
        assert isinstance(app.screen, TelaConfiguracao)
        assert app.screen.query_one("#dias", Input).value == "30"
        await piloto.press("i", "backspace", "backspace", "7", "enter")
        assert "7 dias" in _texto(app, "#mensagem")
    assert servico.dias_alerta() == 7


async def test_antecedencia_invalida(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-074: valor fora da faixa mostra o erro e não grava (REQ-007 CA-1)."""
    async with app.run_test() as piloto:
        await piloto.press("c", "i", *"999", "enter")
        assert "365" in _texto(app, "#mensagem")
    assert servico.dias_alerta() == 30


async def test_painel_mostra_resumo(app: StockWatchApp, com_estoque: ServicoEstoque) -> None:
    """TEST-TUI-075: produtos, unidades, vencidos e perto de vencer (REQ-009 CA-1)."""
    async with app.run_test():
        resumo = _texto(app, "#resumo")
        for trecho in ["Produtos: 3", "Unidades: 21", "Vencidos: 1", "Perto de vencer: 2"]:
            assert trecho in resumo


async def test_painel_se_atualiza_ao_voltar(app: StockWatchApp, servico: ServicoEstoque) -> None:
    """TEST-TUI-076: ao voltar ao painel, os números refletem a última operação."""
    servico.cadastrar_produto("Leite")
    async with app.run_test() as piloto:
        assert "Unidades: 0" in _texto(app, "#resumo")
        await piloto.press("e", "i", *"Leite", "tab", "6", "enter", "escape")
        assert "Unidades: 6" in _texto(app, "#resumo")


async def test_painel_mostra_todos_os_atalhos(app: StockWatchApp) -> None:
    """TEST-TUI-077: cada tela é alcançável por uma tecla indicada no painel (REQ-009 CA-2)."""
    async with app.run_test():
        atalhos = _texto(app, "#atalhos")
        for tecla in ["p", "e", "s", "t", "v", "c", "q"]:
            assert f"{tecla} " in atalhos


async def test_resumo_ocupa_a_largura_e_centraliza_o_texto(app: StockWatchApp) -> None:
    """TEST-TUI-078: o quadro do painel vai de ponta a ponta, com o texto centralizado."""
    async with app.run_test(size=(100, 30)):
        resumo = app.screen.query_one("#resumo")
        assert resumo.outer_size.width >= 100 - 4
        assert resumo.styles.text_align == "center"
