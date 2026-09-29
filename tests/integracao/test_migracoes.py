"""SUITE-INT: atomicidade das migrações (DT-001)."""

import sqlite3

import pytest

from stockwatch.persistencia.migracoes import migrar


def test_migracao_com_erro_nao_deixa_nada_pela_metade() -> None:
    """TEST-INT-012: um comando inválido desfaz a migração inteira e mantém a versão."""
    conexao = sqlite3.connect(":memory:", isolation_level=None)
    quebrada = "CREATE TABLE parcial (id INTEGER); INSERT INTO inexistente VALUES (1)"
    with pytest.raises(sqlite3.OperationalError):
        migrar(conexao, (quebrada,))
    assert conexao.execute("PRAGMA user_version").fetchone()[0] == 0
    tabelas = conexao.execute("SELECT name FROM sqlite_master WHERE name = 'parcial'")
    assert tabelas.fetchall() == []
