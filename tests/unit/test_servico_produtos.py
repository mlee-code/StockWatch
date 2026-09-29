"""SUITE-UNIT: cadastro e listagem de produtos no serviço (REQ-001, REQ-002)."""

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import NomeInvalido, ProdutoDuplicado
from tests.fakes import UnidadeDeTrabalhoEmMemoria


@pytest.fixture
def banco() -> UnidadeDeTrabalhoEmMemoria:
    return UnidadeDeTrabalhoEmMemoria()


@pytest.fixture
def servico(banco: UnidadeDeTrabalhoEmMemoria) -> ServicoEstoque:
    return ServicoEstoque(lambda: banco)


def test_cadastra_produto_sem_categoria(servico: ServicoEstoque) -> None:
    """TEST-UNIT-010: produto cadastrado aparece na listagem com saldo zero (REQ-001, 002)."""
    criado = servico.cadastrar_produto("Leite integral")
    assert criado.nome == "Leite integral"
    assert criado.categoria is None
    assert servico.listar_produtos() == [criado]
    assert criado.saldo == 0


def test_cadastra_produto_com_categoria(servico: ServicoEstoque) -> None:
    """TEST-UNIT-011: a categoria é opcional e guardada quando informada (REQ-001 CA-3)."""
    assert servico.cadastrar_produto("Leite", " Laticínios ").categoria == "Laticínios"


def test_categoria_em_branco_equivale_a_nenhuma(servico: ServicoEstoque) -> None:
    """TEST-UNIT-012: categoria só com espaços é tratada como ausente (REQ-001 CA-3)."""
    assert servico.cadastrar_produto("Leite", "   ").categoria is None


def test_rejeita_nome_repetido_sem_diferenciar_caixa(servico: ServicoEstoque) -> None:
    """TEST-UNIT-013: nome repetido é rejeitado e nada muda (REQ-001 CA-2, H6)."""
    servico.cadastrar_produto("Leite")
    with pytest.raises(ProdutoDuplicado, match="Leite"):
        servico.cadastrar_produto("  LEITE ")
    assert len(servico.listar_produtos()) == 1


def test_rejeita_nome_invalido_sem_gravar(
    servico: ServicoEstoque, banco: UnidadeDeTrabalhoEmMemoria
) -> None:
    """TEST-UNIT-014: nome inválido é rejeitado sem confirmar a unidade de trabalho."""
    with pytest.raises(NomeInvalido):
        servico.cadastrar_produto("   ")
    assert banco.confirmacoes == 0


def test_lista_em_ordem_alfabetica_sem_diferenciar_caixa(servico: ServicoEstoque) -> None:
    """TEST-UNIT-015: listagem ordenada por nome (REQ-002 CA-1)."""
    for nome in ["banana", "Abacaxi", "cebola"]:
        servico.cadastrar_produto(nome)
    assert [p.nome for p in servico.listar_produtos()] == ["Abacaxi", "banana", "cebola"]


def test_listagem_vazia(servico: ServicoEstoque) -> None:
    """TEST-UNIT-016: sem produtos, a listagem é vazia (REQ-002 CA-2)."""
    assert servico.listar_produtos() == []
