"""App com serviço sobre repositórios em memória (SUITE-TUI não avalia persistência)."""

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.tui.app import StockWatchApp
from tests.fakes import UnidadeDeTrabalhoEmMemoria


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    return ServicoEstoque(lambda: banco)


@pytest.fixture
def app(servico: ServicoEstoque) -> StockWatchApp:
    return StockWatchApp(servico)
