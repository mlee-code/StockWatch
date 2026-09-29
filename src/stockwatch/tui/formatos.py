"""Formatação de valores para exibição."""

from datetime import date


def data_br(valor: date) -> str:
    return valor.strftime("%d/%m/%Y")
