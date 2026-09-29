"""SUITE-UNIT: saídas no serviço (REQ-004)."""

from datetime import UTC, date, datetime

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ProdutoInexistente, SaldoInsuficiente
from stockwatch.dominio.estoque import MotivoSaida, TipoMovimentacao
from tests.fakes import UnidadeDeTrabalhoEmMemoria

AGORA = datetime(2026, 10, 1, 15, 0, tzinfo=UTC)
HOJE = date(2026, 10, 1)


@pytest.fixture
def banco() -> UnidadeDeTrabalhoEmMemoria:
    return UnidadeDeTrabalhoEmMemoria()


@pytest.fixture
def servico(banco: UnidadeDeTrabalhoEmMemoria) -> ServicoEstoque:
    servico = ServicoEstoque(lambda: banco, agora=lambda: AGORA, hoje=lambda: HOJE)
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 4, date(2026, 9, 30))  # vencido
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1))
    servico.registrar_entrada("Leite", 3, date(2026, 10, 3))
    return servico


def test_venda_por_fefo_atualiza_saldo(servico: ServicoEstoque) -> None:
    """TEST-UNIT-080: venda consome os válidos por FEFO e informa o que saiu (REQ-004)."""
    resumo = servico.registrar_saida("leite", 5, MotivoSaida.VENDA)
    assert (resumo.produto, resumo.quantidade, resumo.motivo) == ("Leite", 5, MotivoSaida.VENDA)
    assert resumo.consumos == ((date(2026, 10, 3), 3), (date(2026, 11, 1), 2))
    assert resumo.saldo == 7
    assert servico.listar_produtos()[0].saldo == 7


def test_descarte_consome_so_vencidos(servico: ServicoEstoque) -> None:
    """TEST-UNIT-081: descarte por vencimento (H2)."""
    resumo = servico.registrar_saida("Leite", 4, MotivoSaida.DESCARTE_VENCIMENTO)
    assert resumo.consumos == ((date(2026, 9, 30), 4),)


def test_saldo_insuficiente_nao_grava(
    servico: ServicoEstoque, banco: UnidadeDeTrabalhoEmMemoria
) -> None:
    """TEST-UNIT-082: rejeição total, nada gravado (REQ-004 CA-4)."""
    antes = len(banco.estado.movimentacoes)
    with pytest.raises(SaldoInsuficiente):
        servico.registrar_saida("Leite", 9, MotivoSaida.VENDA)
    assert len(banco.estado.movimentacoes) == antes
    assert servico.listar_produtos()[0].saldo == 12


def test_saida_registra_movimentacao_com_motivo_e_horario(
    servico: ServicoEstoque, banco: UnidadeDeTrabalhoEmMemoria
) -> None:
    """TEST-UNIT-083: movimentação de saída com motivo e relógio injetado (NFR-004)."""
    servico.registrar_saida("Leite", 1, MotivoSaida.PERDA)
    ultima = banco.estado.movimentacoes[-1]
    assert (ultima.tipo, ultima.motivo, ultima.ocorrida_em) == (
        TipoMovimentacao.SAIDA,
        MotivoSaida.PERDA,
        AGORA,
    )


def test_produto_inexistente(servico: ServicoEstoque) -> None:
    """TEST-UNIT-084: saída só de produto cadastrado."""
    with pytest.raises(ProdutoInexistente):
        servico.registrar_saida("Feijão", 1, MotivoSaida.VENDA)
