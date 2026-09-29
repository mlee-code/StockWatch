"""SUITE-PROP: propriedades do plano FEFO (TESTS.md, SUITE-PROP)."""

from datetime import date, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from stockwatch.dominio.erros import SaldoInsuficiente
from stockwatch.dominio.estoque import Lote, LoteComSaldo, MotivoSaida, ordem_fefo
from stockwatch.dominio.fefo import elegivel, planejar_saida

HOJE = date(2026, 10, 1)

validades = st.one_of(st.none(), st.integers(-60, 60).map(lambda dias: HOJE + timedelta(days=dias)))


@st.composite
def estoques(draw: st.DrawFn) -> list[LoteComSaldo]:
    quantidade = draw(st.integers(0, 12))
    ids = draw(
        st.lists(st.integers(1, 10_000), min_size=quantidade, max_size=quantidade, unique=True)
    )
    return [
        LoteComSaldo(Lote(lote_id, 1, draw(validades)), draw(st.integers(1, 50))) for lote_id in ids
    ]


motivos = st.sampled_from(list(MotivoSaida))
pedidos = st.integers(1, 400)


@settings(max_examples=500)
@given(estoques(), pedidos, motivos)
def test_soma_consumida_e_a_pedida_ou_rejeita(
    lotes: list[LoteComSaldo], pedido: int, motivo: MotivoSaida
) -> None:
    """TEST-PROP-001: entrega exatamente o pedido, ou rejeita se o elegível não basta."""
    disponivel = sum(item.saldo for item in lotes if elegivel(item.lote, motivo, HOJE))
    try:
        plano = planejar_saida(lotes, pedido, motivo, HOJE)
    except SaldoInsuficiente:
        assert disponivel < pedido
    else:
        assert sum(c.quantidade for c in plano) == pedido


@settings(max_examples=500)
@given(estoques(), pedidos, motivos)
def test_nenhum_lote_fica_negativo_nem_se_repete(
    lotes: list[LoteComSaldo], pedido: int, motivo: MotivoSaida
) -> None:
    """TEST-PROP-002: cada consumo cabe no saldo do lote, e cada lote aparece uma vez."""
    saldos = {item.lote.id: item.saldo for item in lotes}
    try:
        plano = planejar_saida(lotes, pedido, motivo, HOJE)
    except SaldoInsuficiente:
        return
    assert all(0 < c.quantidade <= saldos[c.lote_id] for c in plano)
    assert len({c.lote_id for c in plano}) == len(plano)


@settings(max_examples=500)
@given(estoques(), pedidos, motivos)
def test_ordem_fefo_e_so_o_ultimo_lote_parcial(
    lotes: list[LoteComSaldo], pedido: int, motivo: MotivoSaida
) -> None:
    """TEST-PROP-003: consome um prefixo dos elegíveis em ordem FEFO; só o último é parcial."""
    try:
        plano = planejar_saida(lotes, pedido, motivo, HOJE)
    except SaldoInsuficiente:
        return
    elegiveis = sorted(
        (item for item in lotes if elegivel(item.lote, motivo, HOJE)),
        key=lambda item: ordem_fefo(item.lote),
    )
    assert [c.lote_id for c in plano] == [item.lote.id for item in elegiveis[: len(plano)]]
    assert all(c.quantidade == item.saldo for c, item in zip(plano[:-1], elegiveis, strict=False))


@settings(max_examples=500)
@given(estoques(), pedidos)
def test_venda_nunca_toca_vencido_e_descarte_so_vencido(
    lotes: list[LoteComSaldo], pedido: int
) -> None:
    """TEST-PROP-004: H1 e H2 para qualquer estoque."""
    por_id = {item.lote.id: item.lote for item in lotes}

    def vencido(lote: Lote) -> bool:
        return lote.validade is not None and lote.validade < HOJE

    for motivo, deve_ser_vencido in [
        (MotivoSaida.VENDA, False),
        (MotivoSaida.DESCARTE_VENCIMENTO, True),
    ]:
        try:
            plano = planejar_saida(lotes, pedido, motivo, HOJE)
        except SaldoInsuficiente:
            continue
        assert all(vencido(por_id[c.lote_id]) is deve_ser_vencido for c in plano)
