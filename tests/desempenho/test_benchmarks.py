"""SUITE-DES: benchmarks das operações de NFR-003 com pytest-benchmark (DECISION-003).

Rode com:
    pytest -m volume tests/desempenho --benchmark-json=desempenho.json --benchmark-save-data
O JSON alimenta scripts/registrar_desempenho.py, que grava as métricas no metadata.
"""

from datetime import date

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import MotivoSaida

pytestmark = pytest.mark.volume

CONSULTAS = ["painel", "validades", "estoque_atual", "listar_produtos", "historico"]


def test_des_registrar_entrada(benchmark: BenchmarkFixture, servico_volume: ServicoEstoque) -> None:
    """TEST-DES-001: registrar entrada."""
    benchmark.pedantic(
        servico_volume.registrar_entrada,
        args=("Produto 03000", 1, date(2027, 1, 1)),
        rounds=50,
        warmup_rounds=2,
    )


def test_des_registrar_saida(benchmark: BenchmarkFixture, servico_volume: ServicoEstoque) -> None:
    """TEST-DES-002: registrar saída por FEFO."""
    benchmark.pedantic(
        servico_volume.registrar_saida,
        args=("Produto 04000", 1, MotivoSaida.PERDA),
        rounds=50,
        warmup_rounds=2,
    )


@pytest.mark.parametrize("consulta", CONSULTAS)
def test_des_consulta(
    benchmark: BenchmarkFixture, servico_volume: ServicoEstoque, consulta: str
) -> None:
    """TEST-DES-003: consultas das telas."""
    benchmark.pedantic(getattr(servico_volume, consulta), rounds=10, warmup_rounds=1)
