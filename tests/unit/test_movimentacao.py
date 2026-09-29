"""SUITE-UNIT: invariantes de lotes e movimentações (CON-008, DATA_MODEL.md)."""

from datetime import UTC, date, datetime

import pytest

from stockwatch.dominio.erros import ErroDominio, QuantidadeInvalida
from stockwatch.dominio.estoque import (
    Consumo,
    Lote,
    LoteComSaldo,
    MotivoSaida,
    Movimentacao,
    TipoMovimentacao,
)

AGORA = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)


def test_entrada_tem_uma_linha_e_nenhum_motivo() -> None:
    """TEST-UNIT-050: a fábrica de entrada monta a movimentação coerente."""
    mov = Movimentacao.entrada(produto_id=1, lote_id=7, quantidade=5, ocorrida_em=AGORA)
    assert mov.tipo is TipoMovimentacao.ENTRADA
    assert mov.motivo is None
    assert mov.linhas == (Consumo(lote_id=7, quantidade=5),)
    assert mov.quantidade == 5


@pytest.mark.parametrize("quantidade", [0, -1])
def test_consumo_exige_quantidade_positiva(quantidade: int) -> None:
    """TEST-UNIT-051: nenhuma linha movimenta zero ou menos unidades."""
    with pytest.raises(QuantidadeInvalida):
        Consumo(lote_id=1, quantidade=quantidade)


def test_movimentacao_sem_linhas_e_invalida() -> None:
    """TEST-UNIT-052: toda movimentação toca ao menos um lote."""
    with pytest.raises(ErroDominio):
        Movimentacao(TipoMovimentacao.SAIDA, 1, (), AGORA, MotivoSaida.VENDA)


def test_saida_exige_motivo_e_entrada_proibe() -> None:
    """TEST-UNIT-053: coerência entre tipo e motivo (REQ-004 CA-1)."""
    linha = (Consumo(1, 1),)
    with pytest.raises(ErroDominio):
        Movimentacao(TipoMovimentacao.SAIDA, 1, linha, AGORA, None)
    with pytest.raises(ErroDominio):
        Movimentacao(TipoMovimentacao.ENTRADA, 1, linha, AGORA, MotivoSaida.PERDA)


def test_entrada_toca_um_unico_lote() -> None:
    """TEST-UNIT-054: cada entrada cria exatamente um lote (REQ-003)."""
    with pytest.raises(ErroDominio):
        Movimentacao(TipoMovimentacao.ENTRADA, 1, (Consumo(1, 1), Consumo(2, 1)), AGORA)


def test_lote_com_saldo_nunca_negativo() -> None:
    """TEST-UNIT-055: invariante de saldo por lote (DATA_MODEL.md, "Derivações")."""
    lote = Lote(id=1, produto_id=1, validade=date(2026, 10, 1))
    assert LoteComSaldo(lote, 0).saldo == 0
    with pytest.raises(ErroDominio):
        LoteComSaldo(lote, -1)


def test_motivos_tem_rotulo_para_o_operador() -> None:
    """TEST-UNIT-056: motivos com texto legível (REQ-004 CA-1)."""
    assert [m.rotulo for m in MotivoSaida] == ["Venda", "Perda", "Descarte por vencimento"]
