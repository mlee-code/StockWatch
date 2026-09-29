"""SUITE-INT: edição de produto no SQLite (REQ-011)."""

from datetime import date
from pathlib import Path

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ProdutoDuplicado
from stockwatch.persistencia.sqlite import BancoSqlite


def test_edicao_persiste_e_preserva_lotes(caminho_banco: Path) -> None:
    """TEST-INT-040: nome, categoria e saldo corretos após reabrir (REQ-011 CA-3)."""
    banco = BancoSqlite(caminho_banco)
    servico = ServicoEstoque(banco.nova_unidade)
    leite = servico.cadastrar_produto("Leite", "Bebidas")
    servico.registrar_entrada("Leite", 4, date(2026, 12, 1))
    servico.editar_produto(leite.id, "Leite integral", "Laticínios")
    banco.fechar()

    reaberto = BancoSqlite(caminho_banco)
    [produto] = ServicoEstoque(reaberto.nova_unidade).listar_produtos()
    assert (produto.nome, produto.categoria, produto.saldo) == ("Leite integral", "Laticínios", 4)
    reaberto.fechar()


def test_duplicado_nao_altera_o_banco(banco: BancoSqlite) -> None:
    """TEST-INT-041: renomear para nome existente não grava nada (REQ-011 CA-2)."""
    servico = ServicoEstoque(banco.nova_unidade)
    servico.cadastrar_produto("Arroz")
    leite = servico.cadastrar_produto("Leite")
    with pytest.raises(ProdutoDuplicado):
        servico.editar_produto(leite.id, "arroz", None)
    assert [p.nome for p in servico.listar_produtos()] == ["Arroz", "Leite"]


def test_categoria_removida(banco: BancoSqlite) -> None:
    """TEST-INT-042: categoria em branco grava NULL."""
    servico = ServicoEstoque(banco.nova_unidade)
    leite = servico.cadastrar_produto("Leite", "Laticínios")
    servico.editar_produto(leite.id, "Leite", "")
    assert servico.listar_produtos()[0].categoria is None
