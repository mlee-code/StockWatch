"""SUITE-INT: migração e repositório de produtos sobre SQLite real."""

import sqlite3
from pathlib import Path

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ProdutoDuplicado
from stockwatch.dominio.valores import NomeValido
from stockwatch.persistencia.sqlite import BancoSqlite


def test_migracao_leva_banco_novo_a_versao_atual(caminho_banco: Path) -> None:
    """TEST-INT-001 / DT-001: banco novo chega a user_version 1; reabrir não reaplica."""
    BancoSqlite(caminho_banco).fechar()
    BancoSqlite(caminho_banco).fechar()
    with sqlite3.connect(caminho_banco) as conexao:
        assert conexao.execute("PRAGMA user_version").fetchone()[0] == 1


def test_chaves_estrangeiras_ativas(banco: BancoSqlite) -> None:
    """TEST-INT-002: PRAGMA foreign_keys vale na conexão (ENGINEERING_PRACTICES)."""
    assert banco.conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_produto_persiste_entre_aberturas(caminho_banco: Path) -> None:
    """TEST-INT-003 / DT-008: dados sobrevivem ao fechamento (REQ-010 CA-1)."""
    banco = BancoSqlite(caminho_banco)
    ServicoEstoque(banco.nova_unidade).cadastrar_produto("Leite", "Laticínios")
    banco.fechar()

    reaberto = BancoSqlite(caminho_banco)
    [produto] = ServicoEstoque(reaberto.nova_unidade).listar_produtos()
    reaberto.fechar()
    assert (produto.nome, produto.categoria, produto.saldo) == ("Leite", "Laticínios", 0)


def test_sem_confirmar_nada_e_gravado(banco: BancoSqlite) -> None:
    """TEST-INT-004 / DT-007: sair da unidade sem confirmar faz rollback (REQ-010 CA-2)."""
    with banco.nova_unidade() as uow:
        uow.produtos.adicionar(NomeValido("Leite"), None)
    assert ServicoEstoque(banco.nova_unidade).listar_produtos() == []


def test_excecao_dentro_da_unidade_faz_rollback(banco: BancoSqlite) -> None:
    """TEST-INT-005 / DT-007: exceção no meio do caso de uso não deixa nada gravado."""
    with pytest.raises(RuntimeError), banco.nova_unidade() as uow:
        uow.produtos.adicionar(NomeValido("Leite"), None)
        raise RuntimeError("falha simulada")
    assert ServicoEstoque(banco.nova_unidade).listar_produtos() == []


@pytest.mark.parametrize("repetido", ["LEITE", "leite", "Leite"])
def test_duplicado_rejeitado_pelo_servico(banco: BancoSqlite, repetido: str) -> None:
    """TEST-INT-006 / DT-003: nome repetido com qualquer caixa é rejeitado (H6)."""
    servico = ServicoEstoque(banco.nova_unidade)
    servico.cadastrar_produto("Leite")
    with pytest.raises(ProdutoDuplicado):
        servico.cadastrar_produto(repetido)


def test_duplicado_nao_ascii_rejeitado_pelo_proprio_banco(banco: BancoSqlite) -> None:
    """TEST-INT-007 / DT-003: a unicidade vale no banco também para letras acentuadas."""
    with banco.nova_unidade() as uow:
        uow.produtos.adicionar(NomeValido("Éclair"), None)
        with pytest.raises(sqlite3.IntegrityError):
            uow.produtos.adicionar(NomeValido("éCLAIR"), None)


def test_categoria_reaproveitada_pelo_nome(banco: BancoSqlite) -> None:
    """TEST-INT-008: a mesma categoria, em qualquer caixa, vira uma única linha (REQ-001 CA-3)."""
    servico = ServicoEstoque(banco.nova_unidade)
    servico.cadastrar_produto("Leite", "Laticínios")
    servico.cadastrar_produto("Queijo", "LATICÍNIOS")
    assert banco.conexao.execute("SELECT count(*) FROM categoria").fetchone()[0] == 1


def test_listagem_ordenada_sem_diferenciar_caixa(banco: BancoSqlite) -> None:
    """TEST-INT-009 / DT-009: ordem alfabética (REQ-002 CA-1)."""
    servico = ServicoEstoque(banco.nova_unidade)
    for nome in ["banana", "Abacaxi", "cebola"]:
        servico.cadastrar_produto(nome)
    assert [p.nome for p in servico.listar_produtos()] == ["Abacaxi", "banana", "cebola"]


def test_integridade_do_banco(banco: BancoSqlite) -> None:
    """TEST-INT-010 / DT-002: integridade e chaves estrangeiras consistentes."""
    ServicoEstoque(banco.nova_unidade).cadastrar_produto("Leite", "Laticínios")
    assert banco.conexao.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert banco.conexao.execute("PRAGMA foreign_key_check").fetchall() == []
