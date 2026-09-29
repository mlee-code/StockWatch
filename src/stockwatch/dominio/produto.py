"""Entidade Produto."""

from dataclasses import dataclass

from stockwatch.dominio.valores import NomeValido


@dataclass(frozen=True, slots=True)
class Produto:
    """Item que o comércio controla; identidade dada pelo `id` persistido."""

    id: int
    nome: NomeValido
    categoria: NomeValido | None = None
