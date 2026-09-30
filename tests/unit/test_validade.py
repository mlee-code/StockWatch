"""SUITE-UNIT: classificação de validade e antecedência do alerta (REQ-006, REQ-007)."""

from datetime import date

import pytest

from stockwatch.dominio.erros import DiasAlertaInvalido
from stockwatch.dominio.leitura import ler_dias_alerta
from stockwatch.dominio.validade import Situacao, classificar

HOJE = date(2026, 10, 1)


@pytest.mark.parametrize(
    ("validade", "situacao"),
    [
        (date(2026, 9, 30), Situacao.VENCIDO),
        (date(2026, 10, 1), Situacao.PERTO),
        (date(2026, 10, 31), Situacao.PERTO),
        (date(2026, 11, 1), Situacao.OK),
        (None, Situacao.SEM_VALIDADE),
    ],
)
def test_classifica_com_30_dias(validade: date | None, situacao: Situacao) -> None:
    """TEST-UNIT-100: vencido antes de hoje; perto de 0 a N dias (REQ-006 CA-1, CA-2, H5)."""
    assert classificar(validade, HOJE, 30) is situacao


def test_com_zero_dias_so_hoje_e_perto() -> None:
    """TEST-UNIT-101: N = 0 alerta só o que vence hoje (REQ-007 CA-1)."""
    assert classificar(HOJE, HOJE, 0) is Situacao.PERTO
    assert classificar(date(2026, 10, 2), HOJE, 0) is Situacao.OK


@pytest.mark.parametrize("situacao", [Situacao.VENCIDO, Situacao.PERTO])
def test_so_vencido_e_perto_sao_alertas(situacao: Situacao) -> None:
    """TEST-UNIT-102: somente as duas situações geram alerta (REQ-006 CA-3)."""
    assert situacao.e_alerta
    assert not Situacao.OK.e_alerta
    assert not Situacao.SEM_VALIDADE.e_alerta


@pytest.mark.parametrize(("texto", "dias"), [("0", 0), (" 30 ", 30), ("365", 365)])
def test_le_dias_alerta(texto: str, dias: int) -> None:
    """TEST-UNIT-103: inteiro de 0 a 365 (REQ-007 CA-1)."""
    assert ler_dias_alerta(texto) == dias


@pytest.mark.parametrize("texto", ["", "-1", "366", "trinta", "1.5"])
def test_rejeita_dias_invalidos(texto: str) -> None:
    """TEST-UNIT-104: fora da faixa ou não inteiro é rejeitado."""
    with pytest.raises(DiasAlertaInvalido, match="365"):
        ler_dias_alerta(texto)
