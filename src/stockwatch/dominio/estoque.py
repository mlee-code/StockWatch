"""Lotes e movimentações: o estoque é derivado das movimentações de cada lote."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from stockwatch.dominio.erros import (
    MovimentacaoInvalida,
    QuantidadeInvalida,
    SaldoInvalido,
)
from stockwatch.dominio.valores import NomeValido


class TipoMovimentacao(StrEnum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class MotivoSaida(StrEnum):
    """Motivo obrigatório de toda saída (REQ-004 CA-1)."""

    VENDA = "venda"
    PERDA = "perda"
    DESCARTE_VENCIMENTO = "descarte_vencimento"

    @property
    def rotulo(self) -> str:
        return {
            MotivoSaida.VENDA: "Venda",
            MotivoSaida.PERDA: "Perda",
            MotivoSaida.DESCARTE_VENCIMENTO: "Descarte por vencimento",
        }[self]


@dataclass(frozen=True, slots=True)
class Lote:
    """Unidades de um produto que entraram juntas; validade None não vence (CON-008)."""

    id: int
    produto_id: int
    validade: date | None
    fornecedor: NomeValido | None = None


def ordem_fefo(lote: Lote) -> tuple[bool, date, int]:
    """Chave FEFO: validade mais próxima primeiro, sem validade por último,
    e lote mais antigo no empate (REQ-004 CA-2, H4, DECISION-007)."""
    return (lote.validade is None, lote.validade or date.max, lote.id)


@dataclass(frozen=True, slots=True)
class LoteComSaldo:
    lote: Lote
    saldo: int

    def __post_init__(self) -> None:
        if self.saldo < 0:
            raise SaldoInvalido(f"O lote {self.lote.id} ficaria com saldo negativo.")


@dataclass(frozen=True, slots=True)
class Consumo:
    """Quantas unidades uma movimentação tocou em um lote."""

    lote_id: int
    quantidade: int

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise QuantidadeInvalida("A quantidade deve ser um número inteiro maior que zero.")


@dataclass(frozen=True, slots=True)
class Movimentacao:
    tipo: TipoMovimentacao
    produto_id: int
    linhas: tuple[Consumo, ...]
    ocorrida_em: datetime
    motivo: MotivoSaida | None = None

    def __post_init__(self) -> None:
        if not self.linhas:
            raise MovimentacaoInvalida("A movimentação precisa tocar ao menos um lote.")
        if self.tipo is TipoMovimentacao.ENTRADA:
            if self.motivo is not None:
                raise MovimentacaoInvalida("Entrada não tem motivo.")
            if len(self.linhas) != 1:
                raise MovimentacaoInvalida("Entrada cria exatamente um lote.")
        elif self.motivo is None:
            raise MovimentacaoInvalida("Toda saída precisa de um motivo.")

    @classmethod
    def entrada(
        cls, *, produto_id: int, lote_id: int, quantidade: int, ocorrida_em: datetime
    ) -> "Movimentacao":
        return cls(
            TipoMovimentacao.ENTRADA, produto_id, (Consumo(lote_id, quantidade),), ocorrida_em
        )

    @property
    def quantidade(self) -> int:
        return sum(linha.quantidade for linha in self.linhas)
