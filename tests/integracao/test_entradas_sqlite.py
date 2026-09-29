"""SUITE-INT: lotes, movimentações e estoque sobre SQLite real (REQ-003, REQ-005)."""

import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.valores import NomeValido
from stockwatch.persistencia.sqlite import BancoSqlite

AGORA = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)


def _servico(banco: BancoSqlite) -> ServicoEstoque:
    return ServicoEstoque(banco.nova_unidade, agora=lambda: AGORA)


@pytest.fixture
def servico(banco: BancoSqlite) -> ServicoEstoque:
    servico = _servico(banco)
    servico.cadastrar_produto("Leite")
    return servico


def test_entrada_persiste_e_saldo_e_derivado(caminho_banco: Path) -> None:
    """TEST-INT-020 / DT-008: entrada sobrevive ao reinício com o saldo correto."""
    banco = BancoSqlite(caminho_banco)
    servico = _servico(banco)
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1), "Laticínios Sul")
    servico.registrar_entrada("Leite", 2, date(2026, 10, 3))
    banco.fechar()

    reaberto = BancoSqlite(caminho_banco)
    servico = _servico(reaberto)
    [item] = servico.estoque_atual()
    assert (item.produto, item.saldo, item.proxima_validade) == ("Leite", 7, date(2026, 10, 3))
    lotes = servico.lotes_do_produto(item.produto_id)
    assert [(lote.validade, lote.fornecedor, lote.saldo) for lote in lotes] == [
        (date(2026, 10, 3), None, 2),
        (date(2026, 11, 1), "Laticínios Sul", 5),
    ]
    assert servico.listar_produtos()[0].saldo == 7
    reaberto.fechar()


def test_movimentacao_guarda_instante_em_utc(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-021: ocorrida_em em ISO 8601 UTC (DATA_MODEL.md)."""
    servico.registrar_entrada("Leite", 1, date(2026, 10, 1))
    [(tipo, motivo, ocorrida_em)] = banco.conexao.execute(
        "SELECT tipo, motivo, ocorrida_em FROM movimentacao"
    ).fetchall()
    assert (tipo, motivo) == ("entrada", None)
    assert datetime.fromisoformat(ocorrida_em) == AGORA


def test_fornecedor_reaproveitado_pelo_nome(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-022: mesmo fornecedor, em qualquer caixa, é uma única linha (REQ-003 CA-3)."""
    servico.registrar_entrada("Leite", 1, date(2026, 10, 1), "Laticínios Sul")
    servico.registrar_entrada("Leite", 1, date(2026, 10, 1), "LATICÍNIOS SUL")
    assert banco.conexao.execute("SELECT count(*) FROM fornecedor").fetchone()[0] == 1


def test_falha_no_meio_da_entrada_nao_deixa_lote(banco: BancoSqlite) -> None:
    """TEST-INT-023 / DT-007: lote criado sem movimentação confirmada é descartado."""
    _servico(banco).cadastrar_produto("Leite")

    def entrada_interrompida() -> None:
        with banco.nova_unidade() as uow:
            produto = uow.produtos.buscar_por_nome(NomeValido("Leite"))
            assert produto is not None
            uow.lotes.adicionar(produto.id, date(2026, 10, 1), None)
            raise RuntimeError("falha simulada")

    with pytest.raises(RuntimeError):
        entrada_interrompida()
    assert banco.conexao.execute("SELECT count(*) FROM lote").fetchone()[0] == 0


@pytest.mark.parametrize(
    ("comando", "parametros"),
    [
        ("INSERT INTO lote (produto_id, validade) VALUES (1, ?)", ("2026-02-31",)),
        ("INSERT INTO lote (produto_id, validade) VALUES (1, ?)", ("31/10/2026",)),
        ("INSERT INTO lote (produto_id, validade) VALUES (999, ?)", ("2026-10-01",)),
        (
            "INSERT INTO movimentacao (tipo, motivo, produto_id, ocorrida_em) VALUES (?, ?, 1, 'x')",
            ("entrada", "venda"),
        ),
        (
            "INSERT INTO movimentacao (tipo, motivo, produto_id, ocorrida_em) VALUES (?, ?, 1, 'x')",
            ("saida", None),
        ),
        (
            "INSERT INTO movimentacao (tipo, motivo, produto_id, ocorrida_em) VALUES (?, ?, 1, 'x')",
            ("saida", "roubo"),
        ),
    ],
)
def test_restricoes_do_banco_rejeitam_dados_invalidos(
    servico: ServicoEstoque, banco: BancoSqlite, comando: str, parametros: tuple[str | None, ...]
) -> None:
    """TEST-INT-024 / DT-004, DT-005: CHECKs e chaves estrangeiras valem no próprio banco."""
    with pytest.raises(sqlite3.IntegrityError):
        banco.conexao.execute(comando, parametros)


def test_quantidade_zero_rejeitada_pelo_banco(servico: ServicoEstoque, banco: BancoSqlite) -> None:
    """TEST-INT-025 / DT-004: movimentacao_lote.quantidade > 0."""
    servico.registrar_entrada("Leite", 1, date(2026, 10, 1))
    with pytest.raises(sqlite3.IntegrityError):
        banco.conexao.execute(
            "INSERT INTO movimentacao_lote (movimentacao_id, lote_id, quantidade) VALUES (1, 1, 0)"
        )
