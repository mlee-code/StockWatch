"""SUITE-INT: saídas por FEFO sobre SQLite real (REQ-004, DT-006, DT-007)."""

from datetime import UTC, date, datetime

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import SaldoInsuficiente
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.persistencia.sqlite import BancoSqlite

HOJE = date(2026, 10, 1)
AGORA = datetime(2026, 10, 1, 15, 0, tzinfo=UTC)

LOTES_NEGATIVOS = """
SELECT ml.lote_id
FROM movimentacao_lote ml JOIN movimentacao m ON m.id = ml.movimentacao_id
GROUP BY ml.lote_id
HAVING SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade ELSE -ml.quantidade END) < 0
"""


@pytest.fixture
def servico(banco: BancoSqlite) -> ServicoEstoque:
    servico = ServicoEstoque(banco.nova_unidade, agora=lambda: AGORA, hoje=lambda: HOJE)
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 4, date(2026, 9, 30))
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1))
    servico.registrar_entrada("Leite", 3, date(2026, 10, 3))
    servico.registrar_entrada("Leite", 2, None)
    return servico


def test_saida_em_varios_lotes_persiste(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-050: uma movimentação, uma linha por lote, na ordem FEFO (REQ-004 CA-5)."""
    servico.registrar_saida("Leite", 9, MotivoSaida.VENDA)
    linhas = banco.conexao.execute(
        """
        SELECT l.validade, ml.quantidade, m.motivo
        FROM movimentacao m
        JOIN movimentacao_lote ml ON ml.movimentacao_id = m.id
        JOIN lote l ON l.id = ml.lote_id
        WHERE m.tipo = 'saida' ORDER BY l.validade IS NULL, l.validade
        """
    ).fetchall()
    assert linhas == [("2026-10-03", 3, "venda"), ("2026-11-01", 5, "venda"), (None, 1, "venda")]
    assert servico.listar_produtos()[0].saldo == 14 - 9


def test_saldo_insuficiente_nao_deixa_nada(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-051 / DT-007: rejeição não grava movimentação nem linhas."""
    with pytest.raises(SaldoInsuficiente):
        servico.registrar_saida("Leite", 11, MotivoSaida.VENDA)
    saidas = banco.conexao.execute("SELECT count(*) FROM movimentacao WHERE tipo = 'saida'")
    assert saidas.fetchone()[0] == 0


def test_nenhum_lote_negativo_apos_saidas(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-052 / DT-006: invariante de saldo verificado por consulta agregada."""
    servico.registrar_saida("Leite", 4, MotivoSaida.DESCARTE_VENCIMENTO)
    servico.registrar_saida("Leite", 10, MotivoSaida.VENDA)
    assert banco.conexao.execute(LOTES_NEGATIVOS).fetchall() == []
    assert servico.estoque_atual() == []
