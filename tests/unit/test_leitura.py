"""SUITE-UNIT: conversão de texto digitado em valores (REQ-003 CA-1, CA-2)."""

from datetime import date

import pytest

from stockwatch.dominio.erros import DataInvalida, MotivoInvalido, QuantidadeInvalida
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.dominio.leitura import ler_data, ler_data_opcional, ler_motivo, ler_quantidade


@pytest.mark.parametrize(("texto", "esperado"), [("1", 1), (" 12 ", 12), ("1000000", 1_000_000)])
def test_le_quantidade_inteira_positiva(texto: str, esperado: int) -> None:
    """TEST-UNIT-030: inteiros positivos, com espaços nas pontas."""
    assert ler_quantidade(texto) == esperado


@pytest.mark.parametrize("texto", ["", " ", "0", "-3", "2.5", "1,5", "dez", "1e3", "٣"])
def test_rejeita_quantidade_invalida(texto: str) -> None:
    """TEST-UNIT-031: vazio, zero, negativo, fracionário, texto e dígitos não ASCII."""
    with pytest.raises(QuantidadeInvalida):
        ler_quantidade(texto)


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("2026-10-05", date(2026, 10, 5)),
        ("05/10/2026", date(2026, 10, 5)),
        (" 5/1/2027 ", date(2027, 1, 5)),
    ],
)
def test_le_data_nos_dois_formatos(texto: str, esperado: date) -> None:
    """TEST-UNIT-032: AAAA-MM-DD e DD/MM/AAAA (REQ-003 CA-2)."""
    assert ler_data(texto) == esperado


@pytest.mark.parametrize(
    "texto", ["", "31/02/2026", "2026-13-01", "10/2026", "amanhã", "05-10-2026"]
)
def test_rejeita_data_invalida(texto: str) -> None:
    """TEST-UNIT-033: vazia, inexistente ou em formato não aceito."""
    with pytest.raises(DataInvalida):
        ler_data(texto)


@pytest.mark.parametrize("texto", ["", "   "])
def test_data_opcional_em_branco_e_nenhuma(texto: str) -> None:
    """TEST-UNIT-034: validade em branco significa lote que não vence (DECISION-007)."""
    assert ler_data_opcional(texto) is None


def test_data_opcional_preenchida_segue_as_regras() -> None:
    """TEST-UNIT-035: preenchida, a validade é lida e validada como antes (REQ-003 CA-2)."""
    assert ler_data_opcional("05/10/2026") == date(2026, 10, 5)
    with pytest.raises(DataInvalida):
        ler_data_opcional("31/02/2026")


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("", MotivoSaida.VENDA),
        (" v ", MotivoSaida.VENDA),
        ("Venda", MotivoSaida.VENDA),
        ("p", MotivoSaida.PERDA),
        ("PERDA", MotivoSaida.PERDA),
        ("d", MotivoSaida.DESCARTE_VENCIMENTO),
        ("descarte", MotivoSaida.DESCARTE_VENCIMENTO),
        ("Descarte por vencimento", MotivoSaida.DESCARTE_VENCIMENTO),
    ],
)
def test_le_motivo_por_inicial_ou_nome(texto: str, esperado: MotivoSaida) -> None:
    """TEST-UNIT-036: motivo pela inicial ou pelo nome; em branco é venda (UX_UI.md)."""
    assert ler_motivo(texto) is esperado


@pytest.mark.parametrize("texto", ["x", "vendas", "roubo", "descartar tudo"])
def test_rejeita_motivo_desconhecido(texto: str) -> None:
    """TEST-UNIT-037: motivo fora da lista é rejeitado com as opções válidas (REQ-004 CA-1)."""
    with pytest.raises(MotivoInvalido, match="venda"):
        ler_motivo(texto)
