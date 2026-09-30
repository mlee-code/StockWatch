"""SUITE-TUI: histórico de movimentações (REQ-008, NFR-002)."""

from datetime import UTC, date, datetime, timedelta
from itertools import count

import pytest
from textual.widgets import DataTable

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.tui.app import StockWatchApp
from stockwatch.tui.telas.historico import TelaHistorico
from tests.fakes import UnidadeDeTrabalhoEmMemoria

INICIO = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)


def _local(instante: datetime) -> str:
    return instante.astimezone().strftime("%d/%m/%Y %H:%M")


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    minutos = count()
    return ServicoEstoque(
        lambda: banco,
        agora=lambda: INICIO + timedelta(minutes=next(minutos)),
        hoje=lambda: date(2026, 10, 1),
    )


@pytest.fixture
def com_movimentos(servico: ServicoEstoque) -> ServicoEstoque:
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Leite", 5, None)
    servico.registrar_entrada("Arroz", 2, None)
    servico.registrar_saida("Leite", 3, MotivoSaida.PERDA)
    return servico


def _linhas(app: StockWatchApp) -> list[list[str]]:
    tabela = app.screen.query_one(DataTable)
    return [[str(c) for c in tabela.get_row_at(i)] for i in range(tabela.row_count)]


async def test_historico_vazio(app: StockWatchApp) -> None:
    """TEST-TUI-090: `m` abre o histórico; sem movimentações, estado vazio (NFR-002)."""
    async with app.run_test() as piloto:
        await piloto.press("m")
        assert isinstance(app.screen, TelaHistorico)
        assert app.screen.query_one("#vazio").display is True


async def test_historico_do_mais_recente_em_hora_local(
    app: StockWatchApp, com_movimentos: ServicoEstoque
) -> None:
    """TEST-TUI-091: data e hora locais, tipo, motivo, produto e quantidade (REQ-008 CA-1)."""
    async with app.run_test() as piloto:
        await piloto.press("m")
        assert _linhas(app) == [
            [_local(INICIO + timedelta(minutes=2)), "Saída", "Perda", "Leite", "3"],
            [_local(INICIO + timedelta(minutes=1)), "Entrada", "—", "Arroz", "2"],
            [_local(INICIO), "Entrada", "—", "Leite", "5"],
        ]


async def test_historico_do_produto_em_foco(
    app: StockWatchApp, com_movimentos: ServicoEstoque
) -> None:
    """TEST-TUI-092: a partir de uma linha de produto, só as dele (REQ-008 CA-4)."""
    async with app.run_test() as piloto:
        await piloto.press("p", "l", "l", "j", "m")
        assert [linha[3] for linha in _linhas(app)] == ["Leite", "Leite"]
        assert "Leite" in app.screen.sub_title


async def test_esc_volta_ao_painel(app: StockWatchApp) -> None:
    """TEST-TUI-093: `Esc` volta ao painel."""
    async with app.run_test() as piloto:
        await piloto.press("m", "escape")
        assert not isinstance(app.screen, TelaHistorico)
