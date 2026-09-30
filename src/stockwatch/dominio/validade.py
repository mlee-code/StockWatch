"""Situação de validade de um lote: função pura sobre datas (REQ-006, H5)."""

from datetime import date
from enum import StrEnum

DIAS_ALERTA_MAXIMO = 365
DIAS_ALERTA_PADRAO = 30


class Situacao(StrEnum):
    VENCIDO = "vencido"
    PERTO = "perto de vencer"
    OK = "ok"
    SEM_VALIDADE = "sem validade"

    @property
    def e_alerta(self) -> bool:
        return self in (Situacao.VENCIDO, Situacao.PERTO)


def classificar(validade: date | None, hoje: date, dias_alerta: int) -> Situacao:
    """Vencido: validade antes de hoje. Perto: faltam de 0 a `dias_alerta` dias."""
    if validade is None:
        return Situacao.SEM_VALIDADE
    faltam = (validade - hoje).days
    if faltam < 0:
        return Situacao.VENCIDO
    if faltam <= dias_alerta:
        return Situacao.PERTO
    return Situacao.OK
