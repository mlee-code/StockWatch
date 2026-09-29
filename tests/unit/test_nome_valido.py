"""SUITE-UNIT: NomeValido (REQ-001 CA-1)."""

import pytest

from stockwatch.dominio.erros import ErroDominio, NomeInvalido
from stockwatch.dominio.valores import NomeValido


def test_remove_espacos_das_pontas() -> None:
    """TEST-UNIT-001: espaços nas pontas são removidos."""
    assert NomeValido("  Leite integral  ").valor == "Leite integral"


@pytest.mark.parametrize("tamanho", [1, 100])
def test_aceita_tamanhos_limite(tamanho: int) -> None:
    """TEST-UNIT-002: 1 e 100 caracteres são aceitos."""
    assert len(NomeValido("a" * tamanho).valor) == tamanho


@pytest.mark.parametrize("texto", ["", "   ", "a" * 101])
def test_rejeita_vazio_e_longo(texto: str) -> None:
    """TEST-UNIT-003: vazio, só espaços e mais de 100 caracteres são rejeitados."""
    with pytest.raises(NomeInvalido):
        NomeValido(texto)


def test_erro_e_de_dominio_e_tem_mensagem_para_o_operador() -> None:
    """TEST-UNIT-004: o erro é um ErroDominio com mensagem em português."""
    with pytest.raises(ErroDominio, match="nome"):
        NomeValido("")


def test_igualdade_ignora_maiusculas() -> None:
    """TEST-UNIT-005: nomes iguais sem distinguir caixa são o mesmo nome (H6)."""
    assert NomeValido("Leite") == NomeValido("LEITE")
    assert hash(NomeValido("Leite")) == hash(NomeValido("leite"))


def test_e_imutavel() -> None:
    """TEST-UNIT-006: o valor não pode ser alterado."""
    nome = NomeValido("Leite")
    with pytest.raises(AttributeError):
        nome.valor = "Outro"  # type: ignore[misc]
