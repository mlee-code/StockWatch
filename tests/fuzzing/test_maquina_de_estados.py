"""SUITE-FUZZ: sequências aleatórias de operações no serviço sobre SQLite real.

A máquina de estados do Hypothesis cadastra, edita, exclui, dá entrada, dá
saída e avança o calendário em qualquer ordem, e confere após cada passo as
invariantes do estoque contra um modelo simples mantido pelo teste.
"""

from datetime import date, timedelta
from pathlib import Path

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, precondition, rule

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.dominio.erros import ErroDominio
from stockwatch.dominio.estoque import MotivoSaida
from stockwatch.persistencia.sqlite import BancoSqlite

NOMES = st.sampled_from(["Leite", "leite", "Arroz", "Éclair", "ÉCLAIR", " Café ", "Pão"])
VALIDADES = st.one_of(st.none(), st.integers(-10, 40))

LOTES_NEGATIVOS = """
SELECT ml.lote_id FROM movimentacao_lote ml
JOIN movimentacao m ON m.id = ml.movimentacao_id
GROUP BY ml.lote_id
HAVING SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade ELSE -ml.quantidade END) < 0
"""


class OperacoesDeEstoque(RuleBasedStateMachine):
    @initialize()
    def abrir_banco(self) -> None:
        self.hoje = date(2026, 10, 1)
        self.banco = BancoSqlite(Path(":memory:"))
        self.servico = ServicoEstoque(self.banco.nova_unidade, hoje=lambda: self.hoje)
        self.saldo_esperado: dict[str, int] = {}

    def teardown(self) -> None:
        self.banco.fechar()

    def _produto(self, nome: str) -> str | None:
        return next(
            (p for p in self.saldo_esperado if p.casefold() == nome.strip().casefold()), None
        )

    @rule(nome=NOMES)
    def cadastrar(self, nome: str) -> None:
        try:
            criado = self.servico.cadastrar_produto(nome)
        except ErroDominio:
            assert self._produto(nome) is not None
        else:
            self.saldo_esperado[criado.nome] = 0

    @precondition(lambda self: bool(self.saldo_esperado))
    @rule(dados=st.data(), quantidade=st.integers(-2, 20), dias=VALIDADES)
    def entrada(self, dados: st.DataObject, quantidade: int, dias: int | None) -> None:
        nome = dados.draw(st.sampled_from(sorted(self.saldo_esperado)))
        validade = None if dias is None else self.hoje + timedelta(days=dias)
        try:
            self.servico.registrar_entrada(nome, quantidade, validade)
        except ErroDominio:
            assert quantidade <= 0
        else:
            self.saldo_esperado[nome] += quantidade

    @precondition(lambda self: bool(self.saldo_esperado))
    @rule(
        dados=st.data(), quantidade=st.integers(-2, 30), motivo=st.sampled_from(list(MotivoSaida))
    )
    def saida(self, dados: st.DataObject, quantidade: int, motivo: MotivoSaida) -> None:
        nome = dados.draw(st.sampled_from(sorted(self.saldo_esperado)))
        try:
            resumo = self.servico.registrar_saida(nome, quantidade, motivo)
        except ErroDominio:
            pass
        else:
            assert sum(q for _, q in resumo.consumos) == quantidade
            self.saldo_esperado[nome] -= quantidade

    @precondition(lambda self: bool(self.saldo_esperado))
    @rule(dados=st.data(), novo=NOMES)
    def renomear(self, dados: st.DataObject, novo: str) -> None:
        antigo = dados.draw(st.sampled_from(sorted(self.saldo_esperado)))
        produto_id = next(p.id for p in self.servico.listar_produtos() if p.nome == antigo)
        try:
            editado = self.servico.editar_produto(produto_id, novo)
        except ErroDominio:
            dono = self._produto(novo)
            assert dono is not None
            assert dono != antigo
        else:
            self.saldo_esperado[editado.nome] = self.saldo_esperado.pop(antigo)

    @precondition(lambda self: bool(self.saldo_esperado))
    @rule(dados=st.data())
    def excluir(self, dados: st.DataObject) -> None:
        nome = dados.draw(st.sampled_from(sorted(self.saldo_esperado)))
        produto_id = next(p.id for p in self.servico.listar_produtos() if p.nome == nome)
        teve_movimento = any(h.produto == nome for h in self.servico.historico(limite=10_000))
        try:
            self.servico.excluir_produto(produto_id)
        except ErroDominio:
            assert teve_movimento
        else:
            assert not teve_movimento
            del self.saldo_esperado[nome]

    @rule(dias=st.integers(1, 20))
    def avancar_calendario(self, dias: int) -> None:
        self.hoje += timedelta(days=dias)

    @invariant()
    def saldos_conferem_com_o_modelo(self) -> None:
        if not hasattr(self, "servico"):
            return
        reais = {p.nome: p.saldo for p in self.servico.listar_produtos()}
        assert reais == self.saldo_esperado

    @invariant()
    def nenhum_lote_negativo_e_banco_integro(self) -> None:
        if not hasattr(self, "banco"):
            return
        conexao = self.banco.conexao
        assert conexao.execute(LOTES_NEGATIVOS).fetchall() == []
        assert conexao.execute("PRAGMA foreign_key_check").fetchall() == []

    @invariant()
    def painel_e_validades_coerentes(self) -> None:
        if not hasattr(self, "servico"):
            return
        painel = self.servico.painel()
        assert painel.unidades == sum(self.saldo_esperado.values())
        alertas = self.servico.validades()
        assert all(a.saldo > 0 and a.situacao.e_alerta for a in alertas)
        assert painel.lotes_vencidos + painel.lotes_perto == len(alertas)


OperacoesDeEstoque.TestCase.settings = settings(
    max_examples=200, stateful_step_count=50, deadline=None
)
test_operacoes_de_estoque = OperacoesDeEstoque.TestCase
test_operacoes_de_estoque.__doc__ = "TEST-FUZZ-002: invariantes sob sequências aleatórias."
