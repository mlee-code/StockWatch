"""SUITE-INT: exclusão de produto no SQLite (REQ-013, DECISION-010)."""

from datetime import date

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ProdutoComMovimentacoes
from stockwatch.persistencia.sqlite import BancoSqlite


def test_exclusao_remove_a_linha(banco: BancoSqlite) -> None:
    """TEST-INT-060: produto sem uso é removido; categoria permanece (DECISION-010)."""
    servico = ServicoEstoque(banco.nova_unidade)
    leite = servico.cadastrar_produto("Leite", "Laticínios")
    servico.excluir_produto(leite.id)
    assert banco.conexao.execute("SELECT count(*) FROM produto").fetchone()[0] == 0
    assert banco.conexao.execute("SELECT count(*) FROM categoria").fetchone()[0] == 1
    assert banco.conexao.execute("PRAGMA foreign_key_check").fetchall() == []


def test_com_movimentacoes_nada_muda(banco: BancoSqlite) -> None:
    """TEST-INT-061: rejeição preserva produto, lote e movimentação (REQ-013 CA-2)."""
    servico = ServicoEstoque(banco.nova_unidade)
    leite = servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, date(2027, 1, 1))
    with pytest.raises(ProdutoComMovimentacoes):
        servico.excluir_produto(leite.id)
    contagens = [
        banco.conexao.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]
        for tabela in ("produto", "lote", "movimentacao", "movimentacao_lote")
    ]
    assert contagens == [1, 1, 1, 1]
