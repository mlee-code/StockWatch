"""SUITE-VOL: metas de NFR-003 com 10 mil produtos e 1 milhão de movimentações.

Rode com `pytest -m volume`. Os tempos são medidos no próprio teste (p95 de várias
execuções); as métricas detalhadas vão para o metadata pela SUITE-DES (DECISION-003).
"""

import statistics
import time
from collections.abc import Callable
from datetime import date

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.persistencia.sqlite import BancoSqlite
from tests.volume.gerador import LOTES_POR_PRODUTO, PRODUTOS, SAIDAS_POR_PRODUTO

pytestmark = pytest.mark.volume

LOTES_NEGATIVOS = """
SELECT ml.lote_id FROM movimentacao_lote ml
JOIN movimentacao m ON m.id = ml.movimentacao_id
GROUP BY ml.lote_id
HAVING SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade ELSE -ml.quantidade END) < 0
"""


def _p95(operacao: Callable[[], object], repeticoes: int) -> float:
    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        operacao()
        tempos.append(time.perf_counter() - inicio)
    return statistics.quantiles(tempos, n=20)[-1] if repeticoes >= 2 else tempos[0]


def test_volume_gerado(banco_volume: BancoSqlite) -> None:
    """TEST-VOL-001: o banco tem o volume de NFR-003."""
    conexao = banco_volume.conexao
    assert conexao.execute("SELECT count(*) FROM produto").fetchone()[0] == PRODUTOS
    movimentacoes = conexao.execute("SELECT count(*) FROM movimentacao").fetchone()[0]
    assert movimentacoes == PRODUTOS * (LOTES_POR_PRODUTO + SAIDAS_POR_PRODUTO) == 1_000_000


def test_invariante_de_saldo_no_banco_inteiro(banco_volume: BancoSqlite) -> None:
    """TEST-VOL-002 / DT-006: nenhum lote negativo em 1 milhão de movimentações."""
    assert banco_volume.conexao.execute(LOTES_NEGATIVOS).fetchall() == []


def test_entrada_abaixo_de_50_ms(servico_volume: ServicoEstoque) -> None:
    """TEST-VOL-003 / NFR-003: registrar entrada, p95 < 50 ms."""
    p95 = _p95(lambda: servico_volume.registrar_entrada("Produto 05000", 1, date(2027, 1, 1)), 50)
    assert p95 < 0.050, f"p95 = {p95 * 1000:.1f} ms"


def test_saida_abaixo_de_50_ms(servico_volume: ServicoEstoque) -> None:
    """TEST-VOL-004 / NFR-003: registrar saída por FEFO, p95 < 50 ms."""
    p95 = _p95(lambda: servico_volume.registrar_saida("Produto 07000", 1, MotivoSaida.PERDA), 50)
    assert p95 < 0.050, f"p95 = {p95 * 1000:.1f} ms"


@pytest.mark.parametrize(
    "consulta", ["estoque_atual", "validades", "painel", "listar_produtos", "historico"]
)
def test_consultas_abaixo_de_1_s(servico_volume: ServicoEstoque, consulta: str) -> None:
    """TEST-VOL-005 / NFR-003: consultas das telas, p95 < 1 s."""
    p95 = _p95(getattr(servico_volume, consulta), 5)
    assert p95 < 1.0, f"{consulta}: p95 = {p95:.2f} s"


def test_saldo_do_lote_usa_indice(banco_volume: BancoSqlite) -> None:
    """TEST-VOL-006 / DT-010: o saldo por lote não varre movimentacao_lote inteira."""
    plano = banco_volume.conexao.execute(
        """
        EXPLAIN QUERY PLAN
        SELECT SUM(ml.quantidade) FROM movimentacao_lote ml
        JOIN movimentacao m ON m.id = ml.movimentacao_id WHERE ml.lote_id = ?
        """,
        (1,),
    ).fetchall()
    detalhes = " | ".join(str(linha[-1]) for linha in plano)
    assert "USING INDEX idx_movimentacao_lote_lote" in detalhes, detalhes
