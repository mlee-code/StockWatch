"""Banco de volume gerado uma vez por sessão (SUITE-VOL)."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.sqlite import BancoSqlite
from tests.volume.gerador import HOJE, gerar


@pytest.fixture(scope="session")
def caminho_volume(tmp_path_factory: pytest.TempPathFactory) -> Path:
    caminho = tmp_path_factory.mktemp("volume") / "volume.db"
    gerar(caminho)
    return caminho


@pytest.fixture(scope="session")
def banco_volume(caminho_volume: Path) -> Iterator[BancoSqlite]:
    banco = BancoSqlite(caminho_volume)
    yield banco
    banco.fechar()


@pytest.fixture(scope="session")
def servico_volume(banco_volume: BancoSqlite) -> ServicoEstoque:
    return ServicoEstoque(banco_volume.nova_unidade, hoje=lambda: HOJE)
