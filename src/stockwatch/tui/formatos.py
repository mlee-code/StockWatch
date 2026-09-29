"""Formatação de valores para exibição."""

from datetime import date


def data_br(valor: date) -> str:
    return valor.strftime("%d/%m/%Y")


def validade_br(valor: date | None) -> str:
    """Validade para exibição; None é lote que não vence (DECISION-007)."""
    return data_br(valor) if valor else "sem validade"
