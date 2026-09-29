"""SUITE-UNIT: entradas e estoque atual no serviço (REQ-003, REQ-005)."""

from datetime import UTC, date, datetime

import pytest

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import NomeInvalido, ProdutoInexistente, QuantidadeInvalida
from stockwatch.dominio.estoque import TipoMovimentacao
from tests.fakes import UnidadeDeTrabalhoEmMemoria

AGORA = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
OUTUBRO = date(2026, 10, 10)


@pytest.fixture
def banco() -> UnidadeDeTrabalhoEmMemoria:
    return UnidadeDeTrabalhoEmMemoria()


@pytest.fixture
def servico(banco: UnidadeDeTrabalhoEmMemoria) -> ServicoEstoque:
    servico = ServicoEstoque(lambda: banco, agora=lambda: AGORA)
    servico.cadastrar_produto("Leite")
    servico.cadastrar_produto("Arroz")
    return servico


def _saldo(servico: ServicoEstoque, nome: str) -> int:
    return next(p.saldo for p in servico.listar_produtos() if p.nome == nome)


def test_entrada_aumenta_saldo_exatamente(servico: ServicoEstoque) -> None:
    """TEST-UNIT-040: o saldo sobe na quantidade informada (REQ-003 CA-4)."""
    resumo = servico.registrar_entrada("leite", 12, OUTUBRO)
    assert (resumo.produto, resumo.quantidade, resumo.validade, resumo.saldo) == (
        "Leite",
        12,
        OUTUBRO,
        12,
    )
    servico.registrar_entrada("Leite", 3, OUTUBRO)
    assert _saldo(servico, "Leite") == 15
    assert _saldo(servico, "Arroz") == 0


def test_produto_inexistente_e_rejeitado(servico: ServicoEstoque) -> None:
    """TEST-UNIT-041: entrada só para produto cadastrado (REQ-003)."""
    with pytest.raises(ProdutoInexistente, match="Feijão"):
        servico.registrar_entrada("Feijão", 1, OUTUBRO)


@pytest.mark.parametrize("quantidade", [0, -5])
def test_quantidade_invalida_nao_grava(
    servico: ServicoEstoque, banco: UnidadeDeTrabalhoEmMemoria, quantidade: int
) -> None:
    """TEST-UNIT-042: quantidade ≤ 0 é rejeitada e nenhum lote é criado (REQ-003 CA-1)."""
    with pytest.raises(QuantidadeInvalida):
        servico.registrar_entrada("Leite", quantidade, OUTUBRO)
    assert banco.estado.lotes == {}


def test_fornecedor_opcional_e_validado(servico: ServicoEstoque) -> None:
    """TEST-UNIT-043: fornecedor opcional; em branco é ausente; inválido é rejeitado (CA-3)."""
    servico.registrar_entrada("Leite", 1, OUTUBRO, " Laticínios Sul ")
    servico.registrar_entrada("Leite", 1, OUTUBRO, "  ")
    produto_id = servico.listar_produtos()[1].id
    fornecedores = [lote.fornecedor for lote in servico.lotes_do_produto(produto_id)]
    assert fornecedores == ["Laticínios Sul", None]
    with pytest.raises(NomeInvalido):
        servico.registrar_entrada("Leite", 1, OUTUBRO, "x" * 101)


def test_cada_entrada_cria_um_lote(servico: ServicoEstoque) -> None:
    """TEST-UNIT-044: mesma validade, lotes distintos (REQ-003, H4)."""
    primeiro = servico.registrar_entrada("Leite", 1, OUTUBRO)
    segundo = servico.registrar_entrada("Leite", 1, OUTUBRO)
    assert primeiro.lote_id != segundo.lote_id


def test_entrada_registra_movimentacao_com_horario_do_relogio(
    servico: ServicoEstoque, banco: UnidadeDeTrabalhoEmMemoria
) -> None:
    """TEST-UNIT-045: a movimentação guarda o instante do relógio injetado (NFR-004)."""
    servico.registrar_entrada("Leite", 4, OUTUBRO)
    [mov] = banco.estado.movimentacoes
    assert (mov.tipo, mov.quantidade, mov.ocorrida_em) == (TipoMovimentacao.ENTRADA, 4, AGORA)


def test_estoque_atual_so_com_saldo_e_proxima_validade(servico: ServicoEstoque) -> None:
    """TEST-UNIT-046: produtos com saldo, validade mais próxima, ordem alfabética (REQ-005 CA-1)."""
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1))
    servico.registrar_entrada("Leite", 2, date(2026, 10, 3))
    servico.cadastrar_produto("Banana")
    servico.registrar_entrada("Banana", 7, date(2026, 10, 1))
    estoque = servico.estoque_atual()
    assert [(i.produto, i.saldo, i.proxima_validade) for i in estoque] == [
        ("Banana", 7, date(2026, 10, 1)),
        ("Leite", 7, date(2026, 10, 3)),
    ]


def test_lotes_do_produto_por_validade(servico: ServicoEstoque) -> None:
    """TEST-UNIT-047: detalhe dos lotes com saldo, do que vence antes (REQ-005 CA-2)."""
    servico.registrar_entrada("Leite", 5, date(2026, 11, 1))
    servico.registrar_entrada("Leite", 2, date(2026, 10, 3))
    produto_id = servico.estoque_atual()[0].produto_id
    lotes = servico.lotes_do_produto(produto_id)
    assert [(lote.validade, lote.saldo) for lote in lotes] == [
        (date(2026, 10, 3), 2),
        (date(2026, 11, 1), 5),
    ]


def test_estoque_vazio(servico: ServicoEstoque) -> None:
    """TEST-UNIT-048: sem entradas, estoque vazio."""
    assert servico.estoque_atual() == []


def test_entrada_sem_validade(servico: ServicoEstoque) -> None:
    """TEST-UNIT-049: lote sem validade entra no estoque sem próxima validade (DECISION-007)."""
    resumo = servico.registrar_entrada("Leite", 4, None)
    assert resumo.validade is None
    [item] = servico.estoque_atual()
    assert (item.saldo, item.proxima_validade) == (4, None)


def test_lotes_sem_validade_vem_por_ultimo(servico: ServicoEstoque) -> None:
    """TEST-UNIT-057: sem validade depois dos datados; a próxima validade os ignora."""
    servico.registrar_entrada("Leite", 1, None)
    servico.registrar_entrada("Leite", 2, date(2026, 12, 1))
    produto_id = servico.estoque_atual()[0].produto_id
    assert [lote.validade for lote in servico.lotes_do_produto(produto_id)] == [
        date(2026, 12, 1),
        None,
    ]
    assert servico.estoque_atual()[0].proxima_validade == date(2026, 12, 1)
