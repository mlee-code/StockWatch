"""Dados imutáveis entregues à interface; não expõem entidades do domínio."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResumoProduto:
    """Produto com saldo atual, para listagens (REQ-002)."""

    id: int
    nome: str
    categoria: str | None
    saldo: int
