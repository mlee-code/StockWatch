"""Conversão pura de texto digitado em valores do domínio.

Toda entrada inválida vira um ErroDominio com mensagem para o operador,
nunca outra exceção (SUITE-FUZZ).
"""

import re
from datetime import date

from stockwatch.dominio.erros import (
    DataInvalida,
    DiasAlertaInvalido,
    MotivoInvalido,
    QuantidadeInvalida,
)
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.dominio.validade import DIAS_ALERTA_MAXIMO

_INTEIRO = re.compile(r"[0-9]+")
_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})", re.ASCII)
_BRASILEIRO = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})", re.ASCII)


def ler_quantidade(texto: str) -> int:
    """Inteiro maior que zero (REQ-003 CA-1, REQ-004 CA-1)."""
    limpo = texto.strip()
    if not _INTEIRO.fullmatch(limpo) or int(limpo) == 0:
        raise QuantidadeInvalida("A quantidade deve ser um número inteiro maior que zero.")
    return int(limpo)


def ler_data(texto: str) -> date:
    """Data em `AAAA-MM-DD` ou `DD/MM/AAAA` (REQ-003 CA-2)."""
    limpo = texto.strip()
    if iso := _ISO.fullmatch(limpo):
        ano, mes, dia = iso.groups()
    elif brasileiro := _BRASILEIRO.fullmatch(limpo):
        dia, mes, ano = brasileiro.groups()
    else:
        raise DataInvalida("Informe a data como DD/MM/AAAA ou AAAA-MM-DD.")
    try:
        return date(int(ano), int(mes), int(dia))
    except ValueError:
        raise DataInvalida(f"A data “{limpo}” não existe.") from None


def ler_data_opcional(texto: str) -> date | None:
    """Validade opcional: em branco, o lote não vence (DECISION-007)."""
    return ler_data(texto) if texto.strip() else None


_MOTIVOS = {
    **dict.fromkeys(["", "v", "venda"], MotivoSaida.VENDA),
    **dict.fromkeys(["p", "perda"], MotivoSaida.PERDA),
    **dict.fromkeys(["d", "descarte", "descarte por vencimento"], MotivoSaida.DESCARTE_VENCIMENTO),
}


def ler_motivo(texto: str) -> MotivoSaida:
    """Motivo pela inicial ou pelo nome; em branco, venda (REQ-004 CA-1, UX_UI.md)."""
    try:
        return _MOTIVOS[" ".join(texto.split()).casefold()]
    except KeyError:
        raise MotivoInvalido(
            "Motivo inválido: use venda (v), perda (p) ou descarte por vencimento (d)."
        ) from None


def ler_dias_alerta(texto: str) -> int:
    """Antecedência do alerta: inteiro de 0 a 365 dias (REQ-007 CA-1)."""
    limpo = texto.strip()
    if not _INTEIRO.fullmatch(limpo) or int(limpo) > DIAS_ALERTA_MAXIMO:
        raise DiasAlertaInvalido(
            f"A antecedência deve ser um número inteiro de 0 a {DIAS_ALERTA_MAXIMO} dias."
        )
    return int(limpo)
