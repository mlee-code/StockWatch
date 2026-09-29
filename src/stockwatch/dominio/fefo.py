"""Plano de saída FEFO: função pura sobre lotes com saldo (REQ-004).

Estilo funcional deliberado: sem estado nem I/O, o plano é inteiramente
determinado pelos argumentos e pode ser verificado por propriedades.
"""

from collections.abc import Iterable
from datetime import date

from stockwatch.dominio.erros import QuantidadeInvalida, SaldoInsuficiente
from stockwatch.dominio.estoque import Consumo, Lote, LoteComSaldo, MotivoSaida, ordem_fefo


def vencido(lote: Lote, hoje: date) -> bool:
    """H5: vence ao fim do dia da validade; lote sem validade nunca vence."""
    return lote.validade is not None and lote.validade < hoje


def elegivel(lote: Lote, motivo: MotivoSaida, hoje: date) -> bool:
    """H1 a H3: quais lotes cada motivo pode consumir."""
    match motivo:
        case MotivoSaida.VENDA:
            return not vencido(lote, hoje)
        case MotivoSaida.DESCARTE_VENCIMENTO:
            return vencido(lote, hoje)
        case MotivoSaida.PERDA:
            return True


def planejar_saida(
    lotes: Iterable[LoteComSaldo], quantidade: int, motivo: MotivoSaida, hoje: date
) -> tuple[Consumo, ...]:
    """Quanto tirar de cada lote, em ordem FEFO, para atender `quantidade`.

    Rejeita a saída inteira (SaldoInsuficiente) se os lotes elegíveis não bastam.
    """
    if quantidade <= 0:
        raise QuantidadeInvalida("A quantidade deve ser um número inteiro maior que zero.")
    candidatos = sorted(
        (item for item in lotes if elegivel(item.lote, motivo, hoje)),
        key=lambda item: ordem_fefo(item.lote),
    )
    disponivel = sum(item.saldo for item in candidatos)
    if disponivel < quantidade:
        raise SaldoInsuficiente(
            f"Saldo insuficiente para {motivo.rotulo.lower()}: "
            f"pedido {quantidade}, disponível {disponivel}."
        )
    plano: list[Consumo] = []
    falta = quantidade
    for item in candidatos:
        if falta == 0:
            break
        tirar = min(falta, item.saldo)
        plano.append(Consumo(item.lote.id, tirar))
        falta -= tirar
    return tuple(plano)
