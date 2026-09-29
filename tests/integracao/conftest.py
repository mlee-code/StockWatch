"""Fixtures com SQLite real em arquivo temporário (SUITE-INT)."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from stockwatch.persistencia.sqlite import BancoSqlite


@pytest.fixture
def caminho_banco(tmp_path: Path) -> Path:
    return tmp_path / "stockwatch.db"


@pytest.fixture
def banco(caminho_banco: Path) -> Iterator[BancoSqlite]:
    banco = BancoSqlite(caminho_banco)
    yield banco
    banco.fechar()
