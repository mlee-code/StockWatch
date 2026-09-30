"""SUITE-INT: histórico de movimentações no SQLite (REQ-008, DT-009)."""

from datetime import UTC, date, datetime, timedelta
from itertools import count

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.estoque import MotivoSaida, TipoMovimentacao
from stockwatch.persistencia.sqlite import BancoSqlite

INICIO = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)


def _servico(banco: BancoSqlite) -> ServicoEstoque:
    minutos = count()
    return ServicoEstoque(
        banco.nova_unidade,
        agora=lambda: INICIO + timedelta(minutes=next(minutos)),
        hoje=lambda: date(2026, 10, 1),
    )


def test_saida_em_varios_lotes_aparece_como_uma_linha(banco: BancoSqlite) -> None:
    """TEST-INT-080: uma saída de vários lotes é uma movimentação com a quantidade total."""
    servico = _servico(banco)
    servico.cadastrar_produto("Leite")
    servico.registrar_entrada("Leite", 2, date(2026, 11, 1))
    servico.registrar_entrada("Leite", 5, date(2026, 12, 1))
    servico.registrar_saida("Leite", 4, MotivoSaida.PERDA)
    [saida, *entradas] = servico.historico()
    assert (saida.tipo, saida.motivo, saida.quantidade, saida.ocorrida_em) == (
        TipoMovimentacao.SAIDA,
        MotivoSaida.PERDA,
        4,
        INICIO + timedelta(minutes=2),
    )
    assert [e.quantidade for e in entradas] == [5, 2]


def test_limite_e_filtro(banco: BancoSqlite) -> None:
    """TEST-INT-081: limite e filtro por produto no banco (REQ-008 CA-3, CA-4)."""
    servico = _servico(banco)
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
    for quantidade in (1, 2, 3):
        servico.registrar_entrada("Leite", quantidade, None)
    servico.registrar_entrada("Arroz", 9, None)
    assert [h.quantidade for h in servico.historico(limite=2)] == [9, 3]
    leite = servico.listar_produtos()[1]
    assert [h.quantidade for h in servico.historico(produto_id=leite.id)] == [3, 2, 1]
