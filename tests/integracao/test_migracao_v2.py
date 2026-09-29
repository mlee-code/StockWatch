"""SUITE-INT: migração 2, validade opcional no lote (DECISION-007, DT-001)."""

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.migracoes import MIGRACOES, migrar
from stockwatch.persistencia.sqlite import BancoSqlite


def test_banco_v1_com_dados_migra_sem_perdas(caminho_banco: Path) -> None:
    """TEST-INT-030: um banco v1 com lotes chega à v2 com os mesmos dados e FKs válidas."""
    conexao = sqlite3.connect(caminho_banco, isolation_level=None)
    conexao.execute("PRAGMA foreign_keys = ON")
    migrar(conexao, MIGRACOES[:1])
    conexao.execute(
        "INSERT INTO produto (nome, nome_chave, criado_em) VALUES ('Leite', 'leite', 'x')"
    )
    conexao.execute("INSERT INTO lote (produto_id, validade) VALUES (1, '2026-10-01')")
    conexao.execute(
        "INSERT INTO movimentacao (tipo, produto_id, ocorrida_em) VALUES ('entrada', 1, 'x')"
    )
    conexao.execute("INSERT INTO movimentacao_lote VALUES (1, 1, 5)")
    conexao.close()

    banco = BancoSqlite(caminho_banco)
    assert banco.conexao.execute("PRAGMA user_version").fetchone()[0] == 2
    assert banco.conexao.execute("PRAGMA foreign_key_check").fetchall() == []
    assert banco.conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    [item] = ServicoEstoque(banco.nova_unidade).estoque_atual()
    assert (item.saldo, item.proxima_validade) == (5, date(2026, 10, 1))
    banco.fechar()


def test_lote_sem_validade_persiste(banco: BancoSqlite) -> None:
    """TEST-INT-031: NULL aceito em lote.validade e lido de volta como sem validade."""
    servico = ServicoEstoque(banco.nova_unidade)
    servico.cadastrar_produto("Vassoura")
    servico.registrar_entrada("Vassoura", 3, None)
    [item] = servico.estoque_atual()
    assert (item.saldo, item.proxima_validade) == (3, None)
    [lote] = servico.lotes_do_produto(item.produto_id)
    assert lote.validade is None


def test_texto_invalido_continua_rejeitado(banco: BancoSqlite) -> None:
    """TEST-INT-032 / DT-004: a v2 mantém o CHECK de data válida quando preenchida."""
    ServicoEstoque(banco.nova_unidade).cadastrar_produto("Leite")
    with pytest.raises(sqlite3.IntegrityError):
        banco.conexao.execute("INSERT INTO lote (produto_id, validade) VALUES (1, '31/10/2026')")
