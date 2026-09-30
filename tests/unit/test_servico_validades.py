"""SUITE-UNIT: validades, antecedência e painel no serviço (REQ-006, 007, 009)."""

from datetime import date

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import DiasAlertaInvalido
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.dominio.validade import Situacao
from tests.fakes import UnidadeDeTrabalhoEmMemoria

HOJE = date(2026, 10, 1)


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    servico = ServicoEstoque(lambda: banco, hoje=lambda: HOJE)
    for nome in ["Arroz", "Leite", "Vassoura"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Leite", 4, date(2026, 9, 28))  # vencido há 3 dias
    servico.registrar_entrada("Leite", 5, date(2026, 10, 11))  # vence em 10 dias
    servico.registrar_entrada("Arroz", 2, date(2026, 10, 1))  # vence hoje
    servico.registrar_entrada("Arroz", 7, date(2027, 6, 1))  # ok
    servico.registrar_entrada("Vassoura", 3, None)  # sem validade
    return servico


def test_lista_so_vencidos_e_perto_do_mais_urgente(servico: ServicoEstoque) -> None:
    """TEST-UNIT-110: alertas ordenados por validade, com dias restantes (REQ-006 CA-3)."""
    alertas = servico.validades()
    assert [(a.produto, a.validade, a.saldo, a.situacao, a.dias) for a in alertas] == [
        ("Leite", date(2026, 9, 28), 4, Situacao.VENCIDO, -3),
        ("Arroz", date(2026, 10, 1), 2, Situacao.PERTO, 0),
        ("Leite", date(2026, 10, 11), 5, Situacao.PERTO, 10),
    ]


def test_lote_sem_saldo_nao_alerta(servico: ServicoEstoque) -> None:
    """TEST-UNIT-111: descartado o vencido, o alerta some (REQ-006 CA-4)."""
    servico.registrar_saida("Leite", 4, MotivoSaida.DESCARTE_VENCIMENTO)
    assert Situacao.VENCIDO not in {a.situacao for a in servico.validades()}


def test_antecedencia_padrao_e_configuravel(servico: ServicoEstoque) -> None:
    """TEST-UNIT-112: padrão 30; com 5 dias, o lote de 10 dias deixa de alertar (REQ-007)."""
    assert servico.dias_alerta() == 30
    assert servico.configurar_dias_alerta(5) == 5
    assert servico.dias_alerta() == 5
    assert [a.dias for a in servico.validades()] == [-3, 0]


@pytest.mark.parametrize("dias", [-1, 366])
def test_antecedencia_fora_da_faixa(servico: ServicoEstoque, dias: int) -> None:
    """TEST-UNIT-113: fora de 0 a 365 é rejeitado e nada muda (REQ-007 CA-1)."""
    with pytest.raises(DiasAlertaInvalido):
        servico.configurar_dias_alerta(dias)
    assert servico.dias_alerta() == 30


def test_painel_resume_estoque_e_alertas(servico: ServicoEstoque) -> None:
    """TEST-UNIT-114: produtos, unidades, vencidos e perto de vencer (REQ-009 CA-1)."""
    painel = servico.painel()
    assert (
        painel.produtos,
        painel.unidades,
        painel.lotes_vencidos,
        painel.lotes_perto,
        painel.dias_alerta,
    ) == (3, 21, 1, 2, 30)


def test_validades_limitadas_aos_mais_urgentes(servico: ServicoEstoque) -> None:
    """TEST-UNIT-115: a lista respeita o limite; o painel continua contando todos (CA-5)."""
    assert [a.dias for a in servico.validades(limite=2)] == [-3, 0]
    painel = servico.painel()
    assert (painel.lotes_vencidos, painel.lotes_perto) == (1, 2)
