"""SUITE-FUZZ: texto arbitrário nos leitores de entrada (TESTS.md, SUITE-FUZZ).

Critério: para qualquer texto, o resultado é um valor válido ou um ErroDominio;
nenhuma outra exceção chega ao operador.
"""

from collections.abc import Callable

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.leitura import (
    ler_data,
    ler_data_opcional,
    ler_dias_alerta,
    ler_motivo,
    ler_quantidade,
)
from stockwatch.dominio.valores import NomeValido

LEITORES: dict[str, Callable[[str], object]] = {
    "quantidade": ler_quantidade,
    "data": ler_data,
    "data_opcional": ler_data_opcional,
    "motivo": ler_motivo,
    "dias_alerta": ler_dias_alerta,
    "nome": NomeValido,
}

# Texto totalmente arbitrário e texto "quase válido", que exercita os caminhos internos.
textos = st.one_of(
    st.text(),
    st.from_regex(r"\s*[0-9]{0,4}[-/][0-9]{0,3}[-/][0-9]{0,5}\s*", fullmatch=True),
    # Inclui dígitos arábico-índicos (U+0660 a U+0669), que str.isdigit() aceitaria.
    st.from_regex(r"\s*-?[0-9\u0660-\u0669]{0,12}\s*", fullmatch=True),
)


@pytest.mark.parametrize("nome", LEITORES)
@settings(max_examples=1000)
@given(texto=textos)
def test_leitor_devolve_valor_ou_erro_de_dominio(nome: str, texto: str) -> None:
    """TEST-FUZZ-001: nenhum texto provoca exceção fora de ErroDominio."""
    try:
        LEITORES[nome](texto)
    except ErroDominio as erro:
        mensagem = str(erro)
    else:
        mensagem = "ok"
    assert mensagem, "todo ErroDominio precisa de mensagem para o operador"
