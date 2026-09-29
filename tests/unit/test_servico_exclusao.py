"""SUITE-UNIT: exclusão de produto no serviço (REQ-013, DECISION-010)."""

from datetime import date

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ProdutoComMovimentacoes, ProdutoInexistente
from tests.fakes import UnidadeDeTrabalhoEmMemoria


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    return ServicoEstoque(lambda: banco)


def test_exclui_produto_sem_movimentacoes(servico: ServicoEstoque) -> None:
    """TEST-UNIT-090: cadastro sem uso pode ser excluído (REQ-013 CA-1)."""
    servico.cadastrar_produto("Arroz")
    leite = servico.cadastrar_produto("Leite")
    assert servico.excluir_produto(leite.id) == "Leite"
    assert [p.nome for p in servico.listar_produtos()] == ["Arroz"]


def test_nome_fica_livre_apos_exclusao(servico: ServicoEstoque) -> None:
    """TEST-UNIT-091: excluído, o nome pode ser cadastrado de novo."""
    leite = servico.cadastrar_produto("Leite")
    servico.excluir_produto(leite.id)
    assert servico.cadastrar_produto("Leite").nome == "Leite"


def test_produto_com_movimentacoes_nao_e_excluido(servico: ServicoEstoque) -> None:
    """TEST-UNIT-092: exclusão rejeitada para preservar o histórico (REQ-013 CA-2)."""
    leite = servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 1, date(2027, 1, 1))
    with pytest.raises(ProdutoComMovimentacoes, match="histórico"):
        servico.excluir_produto(leite.id)
    assert servico.listar_produtos()[0].saldo == 1


def test_produto_inexistente(servico: ServicoEstoque) -> None:
    """TEST-UNIT-093: id inexistente é rejeitado."""
    with pytest.raises(ProdutoInexistente):
        servico.excluir_produto(42)
