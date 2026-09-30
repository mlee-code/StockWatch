"""SUITE-INT: configuração e validades no SQLite (REQ-006, REQ-007, REQ-009)."""

from datetime import date
from pathlib import Path

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.sqlite import BancoSqlite

HOJE = date(2026, 10, 1)


def test_antecedencia_persiste_entre_aberturas(caminho_banco: Path) -> None:
    """TEST-INT-070: padrão 30 no banco novo; valor alterado sobrevive (REQ-007 CA-2)."""
    banco = BancoSqlite(caminho_banco)
    servico = ServicoEstoque(banco.nova_unidade)
    assert servico.dias_alerta() == 30
    servico.configurar_dias_alerta(7)
    banco.fechar()

    reaberto = BancoSqlite(caminho_banco)
    assert ServicoEstoque(reaberto.nova_unidade).dias_alerta() == 7
    reaberto.fechar()


def test_validades_e_painel_com_banco_real(banco: BancoSqlite) -> None:
    """TEST-INT-071 / DT-009: consultas de validade e painel para um cenário conhecido."""
    servico = ServicoEstoque(banco.nova_unidade, hoje=lambda: HOJE)
    for nome in ["Arroz", "Leite"]:
        servico.cadastrar_produto(nome)
    servico.registrar_entrada("Leite", 4, date(2026, 9, 28))
    servico.registrar_entrada("Leite", 5, date(2026, 10, 11))
    servico.registrar_entrada("Arroz", 7, None)
    assert [(a.produto, a.dias) for a in servico.validades()] == [("Leite", -3), ("Leite", 10)]
    painel = servico.painel()
    assert (painel.produtos, painel.unidades, painel.lotes_vencidos, painel.lotes_perto) == (
        2,
        16,
        1,
        1,
    )
