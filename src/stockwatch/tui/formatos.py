"""Formatação de valores para exibição."""

from datetime import date


def data_br(valor: date) -> str:
    return valor.strftime("%d/%m/%Y")


def validade_br(valor: date | None) -> str:
    """Validade para exibição; None é lote que não vence (DECISION-007)."""
    return data_br(valor) if valor else "sem validade"


def descrever_prazo(dias: int) -> str:
    """Situação em texto a partir dos dias até a validade (UX_UI.md, "Validades")."""
    if dias < 0:
        return f"vencido há {-dias} dia{'s' if dias < -1 else ''}"
    if dias == 0:
        return "vence hoje"
    return f"vence em {dias} dia{'s' if dias > 1 else ''}"
