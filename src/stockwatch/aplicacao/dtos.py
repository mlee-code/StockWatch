"""Dados imutáveis entregues à interface; não expõem entidades do domínio."""

from dataclasses import dataclass
from typing import Self

from stockwatch.dominio.produto import Produto


@dataclass(frozen=True, slots=True)
class ResumoProduto:
    """Produto com saldo atual, para listagens (REQ-002)."""

    id: int
    nome: str
    categoria: str | None
    saldo: int

    @classmethod
    def de(cls, produto: Produto, saldo: int) -> Self:
        return cls(
            id=produto.id,
            nome=produto.nome.valor,
            categoria=produto.categoria.valor if produto.categoria else None,
            saldo=saldo,
        )
