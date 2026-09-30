"""SUITE-UNIT: histórico de movimentações no serviço (REQ-008)."""

from datetime import UTC, date, datetime, timedelta
from itertools import count

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import MotivoSaida, TipoMovimentacao
from tests.fakes import UnidadeDeTrabalhoEmMemoria

INICIO = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    minutos = count()
    servico = ServicoEstoque(
        lambda: banco,
        agora=lambda: INICIO + timedelta(minutes=next(minutos)),
        hoje=lambda: date(2026, 10, 1),
    )
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Leite", 5, date(2026, 12, 1))
    servico.registrar_entrada("Leite", 3, date(2026, 11, 1))
    servico.registrar_entrada("Arroz", 2, None)
    servico.registrar_saida("Leite", 4, MotivoSaida.VENDA)
    return servico


def test_mais_recente_primeiro_com_todos_os_campos(servico: ServicoEstoque) -> None:
    """TEST-UNIT-120: data e hora, tipo, motivo, produto e quantidade (REQ-008 CA-1)."""
    historico = servico.historico()
    assert [(h.ocorrida_em, h.tipo, h.motivo, h.produto, h.quantidade) for h in historico] == [
        (INICIO + timedelta(minutes=3), TipoMovimentacao.SAIDA, MotivoSaida.VENDA, "Leite", 4),
        (INICIO + timedelta(minutes=2), TipoMovimentacao.ENTRADA, None, "Arroz", 2),
        (INICIO + timedelta(minutes=1), TipoMovimentacao.ENTRADA, None, "Leite", 3),
        (INICIO, TipoMovimentacao.ENTRADA, None, "Leite", 5),
    ]


def test_limite_de_linhas(servico: ServicoEstoque) -> None:
    """TEST-UNIT-121: devolve só as mais recentes até o limite (REQ-008 CA-3)."""
    assert [h.quantidade for h in servico.historico(limite=2)] == [4, 2]


def test_filtro_por_produto(servico: ServicoEstoque) -> None:
    """TEST-UNIT-122: só as movimentações do produto pedido (REQ-008 CA-4)."""
    arroz = servico.listar_produtos()[0]
    assert [h.produto for h in servico.historico(produto_id=arroz.id)] == ["Arroz"]


def test_historico_vazio() -> None:
    """TEST-UNIT-123: sem movimentações, lista vazia."""
    banco = UnidadeDeTrabalhoEmMemoria()
    assert ServicoEstoque(lambda: banco).historico() == []
