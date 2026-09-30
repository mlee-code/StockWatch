"""SUITE-PROP: classificação de validade para qualquer data e N (TESTS.md)."""

from datetime import date, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from stockwatch.dominio.validade import Situacao, classificar

datas = st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))


@settings(max_examples=500)
@given(datas, datas, st.integers(0, 365))
def test_classificacao_segue_a_definicao(validade: date, hoje: date, dias: int) -> None:
    """TEST-PROP-005: vencido ⇔ validade < hoje; perto ⇔ 0 ≤ faltam ≤ N (H5, REQ-006)."""
    faltam = (validade - hoje).days
    esperado = Situacao.VENCIDO if faltam < 0 else Situacao.PERTO if faltam <= dias else Situacao.OK
    assert classificar(validade, hoje, dias) is esperado


@settings(max_examples=500)
@given(datas, datas, st.integers(0, 364))
def test_aumentar_antecedencia_nunca_tira_alerta(validade: date, hoje: date, dias: int) -> None:
    """TEST-PROP-006: monotonicidade; quem alerta com N também alerta com N + 1."""
    if classificar(validade, hoje, dias).e_alerta:
        assert classificar(validade, hoje, dias + 1).e_alerta


@given(datas)
def test_um_dia_depois_da_validade_esta_vencido(validade: date) -> None:
    """TEST-PROP-007: o produto vence ao fim do dia da validade (H5)."""
    assert classificar(validade, validade, 0) is Situacao.PERTO
    assert classificar(validade, validade + timedelta(days=1), 365) is Situacao.VENCIDO
