"""SUITE-UNIT: edição de produto no serviço (REQ-011)."""

from datetime import date

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import NomeInvalido, ProdutoDuplicado, ProdutoInexistente
from tests.fakes import UnidadeDeTrabalhoEmMemoria


@pytest.fixture
def servico() -> ServicoEstoque:
    banco = UnidadeDeTrabalhoEmMemoria()
    return ServicoEstoque(lambda: banco)


def test_edita_nome_e_categoria(servico: ServicoEstoque) -> None:
    """TEST-UNIT-060: nome e categoria atualizados na listagem (REQ-011)."""
    leite = servico.cadastrar_produto("Leite", "Bebidas")
    editado = servico.editar_produto(leite.id, "Leite integral", "Laticínios")
    assert (editado.nome, editado.categoria) == ("Leite integral", "Laticínios")
    assert servico.listar_produtos() == [editado]


def test_renomear_para_nome_de_outro_e_rejeitado(servico: ServicoEstoque) -> None:
    """TEST-UNIT-061: unicidade vale na edição (REQ-011 CA-2)."""
    servico.cadastrar_produto("Arroz")
    leite = servico.cadastrar_produto("Leite")
    with pytest.raises(ProdutoDuplicado, match="Arroz"):
        servico.editar_produto(leite.id, "ARROZ", None)
    assert [p.nome for p in servico.listar_produtos()] == ["Arroz", "Leite"]


def test_mudar_so_a_caixa_do_proprio_nome_e_permitido(servico: ServicoEstoque) -> None:
    """TEST-UNIT-062: o próprio produto não conta como duplicado (REQ-011 CA-2)."""
    leite = servico.cadastrar_produto("leite")
    assert servico.editar_produto(leite.id, "Leite", None).nome == "Leite"


def test_remove_categoria_em_branco(servico: ServicoEstoque) -> None:
    """TEST-UNIT-063: categoria em branco remove a categoria (REQ-001 CA-3)."""
    leite = servico.cadastrar_produto("Leite", "Laticínios")
    assert servico.editar_produto(leite.id, "Leite", "  ").categoria is None


def test_produto_inexistente(servico: ServicoEstoque) -> None:
    """TEST-UNIT-064: editar um id que não existe é rejeitado."""
    with pytest.raises(ProdutoInexistente):
        servico.editar_produto(999, "Leite", None)


def test_nome_invalido_nao_grava(servico: ServicoEstoque) -> None:
    """TEST-UNIT-065: nome vazio é rejeitado e o produto fica como estava (REQ-011 CA-1)."""
    leite = servico.cadastrar_produto("Leite")
    with pytest.raises(NomeInvalido):
        servico.editar_produto(leite.id, " ", None)
    assert servico.listar_produtos()[0].nome == "Leite"


def test_saldo_preservado(servico: ServicoEstoque) -> None:
    """TEST-UNIT-066: lotes e saldo continuam ligados ao produto (REQ-011 CA-3)."""
    leite = servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 5, date(2026, 12, 1))
    servico.editar_produto(leite.id, "Leite integral", None)
    assert servico.estoque_atual()[0].saldo == 5
    servico.registrar_entrada("Leite integral", 1, None)
    assert servico.listar_produtos()[0].saldo == 6
