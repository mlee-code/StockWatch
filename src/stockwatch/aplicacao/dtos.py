"""Dados imutáveis entregues à interface; não expõem entidades do domínio."""

from dataclasses import dataclass
from datetime import date
from typing import Self

from stockwatch.dominio.estoque import LoteComSaldo
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


@dataclass(frozen=True, slots=True)
class ResumoEntrada:
    """Resultado de uma entrada registrada (REQ-003)."""

    produto: str
    lote_id: int
    quantidade: int
    validade: date | None
    saldo: int


@dataclass(frozen=True, slots=True)
class ItemEstoque:
    """Linha do estoque atual: produto com saldo positivo (REQ-005 CA-1)."""

    produto_id: int
    produto: str
    saldo: int
    proxima_validade: date | None


@dataclass(frozen=True, slots=True)
class SaldoLote:
    """Lote com saldo positivo, para o detalhe de um produto (REQ-005 CA-2)."""

    lote_id: int
    validade: date | None
    fornecedor: str | None
    saldo: int

    @classmethod
    def de(cls, item: LoteComSaldo) -> Self:
        fornecedor = item.lote.fornecedor
        return cls(
            lote_id=item.lote.id,
            validade=item.lote.validade,
            fornecedor=fornecedor.valor if fornecedor else None,
            saldo=item.saldo,
        )
