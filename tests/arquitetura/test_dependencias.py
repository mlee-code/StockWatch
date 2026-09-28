"""SUITE-ARQ: direção das dependências entre camadas (ARCHITECTURE.md, "Guard rails")."""

import ast
from pathlib import Path

import pytest

import stockwatch

RAIZ = Path(stockwatch.__file__).parent
CAMADAS = ("dominio", "aplicacao", "persistencia", "tui")

PROIBIDOS = {
    "dominio": {
        "stockwatch.aplicacao",
        "stockwatch.persistencia",
        "stockwatch.tui",
        "sqlite3",
        "textual",
    },
    "aplicacao": {"stockwatch.persistencia", "stockwatch.tui", "sqlite3", "textual"},
    "persistencia": {"stockwatch.tui", "textual"},
    "tui": {"stockwatch.persistencia", "sqlite3"},
}


def _importados(arquivo: Path) -> set[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            nomes.add(no.module)
    return nomes


def _viola(importado: str, proibido: str) -> bool:
    return importado == proibido or importado.startswith(proibido + ".")


@pytest.mark.parametrize("camada", CAMADAS)
def test_camada_existe(camada: str) -> None:
    """TEST-ARQ-001: cada camada da arquitetura é um pacote."""
    assert (RAIZ / camada / "__init__.py").is_file()


@pytest.mark.parametrize("camada", CAMADAS)
def test_camada_nao_importa_o_que_e_proibido(camada: str) -> None:
    """TEST-ARQ-002: nenhuma camada importa algo proibido para ela."""
    violacoes = [
        f"{arquivo.relative_to(RAIZ)} importa {importado}"
        for arquivo in (RAIZ / camada).rglob("*.py")
        for importado in _importados(arquivo)
        for proibido in PROIBIDOS[camada]
        if _viola(importado, proibido)
    ]
    assert violacoes == []
