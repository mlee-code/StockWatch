"""SUITE-UNIT: plano de saída FEFO (REQ-004 CA-2 a CA-5, H1 a H4, DECISION-007)."""

from datetime import date

import pytest

from stockwatch.dominio.erros import QuantidadeInvalida, SaldoInsuficiente
from stockwatch.dominio.estoque import Consumo, Lote, LoteComSaldo, MotivoSaida
from stockwatch.dominio.fefo import planejar_saida

HOJE = date(2026, 10, 1)
VENDA, PERDA, DESCARTE = MotivoSaida.VENDA, MotivoSaida.PERDA, MotivoSaida.DESCARTE_VENCIMENTO


def _lote(lote_id: int, validade: date | None, saldo: int) -> LoteComSaldo:
    return LoteComSaldo(Lote(lote_id, 1, validade), saldo)


VENCIDO = _lote(1, date(2026, 9, 30), 4)
VENCE_HOJE = _lote(2, date(2026, 10, 1), 3)
FUTURO = _lote(3, date(2026, 12, 1), 5)
SEM_DATA = _lote(4, None, 10)
TODOS = [SEM_DATA, FUTURO, VENCIDO, VENCE_HOJE]


def test_consome_primeiro_o_que_vence_antes() -> None:
    """TEST-UNIT-070: FEFO atravessa lotes até completar (REQ-004 CA-2, CA-5)."""
    plano = planejar_saida(TODOS, 6, PERDA, HOJE)
    assert plano == (Consumo(1, 4), Consumo(2, 2))


def test_venda_ignora_vencidos_e_vende_o_que_vence_hoje() -> None:
    """TEST-UNIT-071: venda só em lotes não vencidos; vencer hoje ainda vale (H1, H5)."""
    assert planejar_saida(TODOS, 4, VENDA, HOJE) == (Consumo(2, 3), Consumo(3, 1))


def test_sem_validade_sai_por_ultimo() -> None:
    """TEST-UNIT-072: lotes sem data depois de todos os datados (DECISION-007)."""
    assert planejar_saida(TODOS, 10, VENDA, HOJE) == (
        Consumo(2, 3),
        Consumo(3, 5),
        Consumo(4, 2),
    )


def test_descarte_so_em_vencidos() -> None:
    """TEST-UNIT-073: descarte por vencimento só consome lotes vencidos (H2)."""
    assert planejar_saida(TODOS, 4, DESCARTE, HOJE) == (Consumo(1, 4),)
    with pytest.raises(SaldoInsuficiente):
        planejar_saida(TODOS, 5, DESCARTE, HOJE)


def test_empate_de_validade_sai_o_mais_antigo() -> None:
    """TEST-UNIT-074: mesma validade, menor id primeiro (H4)."""
    novo, antigo = _lote(9, date(2026, 11, 1), 2), _lote(5, date(2026, 11, 1), 2)
    assert planejar_saida([novo, antigo], 3, VENDA, HOJE) == (Consumo(5, 2), Consumo(9, 1))


def test_saldo_insuficiente_informa_o_disponivel() -> None:
    """TEST-UNIT-075: rejeita a saída inteira e diz quanto há (REQ-004 CA-4)."""
    with pytest.raises(SaldoInsuficiente, match="18"):
        planejar_saida(TODOS, 19, VENDA, HOJE)


@pytest.mark.parametrize("quantidade", [0, -1])
def test_quantidade_invalida(quantidade: int) -> None:
    """TEST-UNIT-076: quantidade ≤ 0 é rejeitada (REQ-004 CA-1)."""
    with pytest.raises(QuantidadeInvalida):
        planejar_saida(TODOS, quantidade, VENDA, HOJE)
