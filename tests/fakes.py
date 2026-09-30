"""Dublês em memória das portas da aplicação, para testes que não avaliam integração."""

from dataclasses import dataclass, field, replace
from datetime import date
from types import TracebackType
from typing import Self

from stockwatch.aplicacao.dtos import ItemEstoque, ResumoProduto
from stockwatch.dominio.estoque import (
    Lote,
    LoteComSaldo,
    Movimentacao,
    TipoMovimentacao,
    ordem_fefo,
)
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.validade import DIAS_ALERTA_PADRAO
from stockwatch.dominio.valores import NomeValido


@dataclass
class EstadoEmMemoria:
    produtos: dict[int, Produto] = field(default_factory=dict)
    lotes: dict[int, Lote] = field(default_factory=dict)
    movimentacoes: list[Movimentacao] = field(default_factory=list)
    dias_alerta: int = DIAS_ALERTA_PADRAO

    def copia(self) -> "EstadoEmMemoria":
        return replace(
            self,
            produtos=dict(self.produtos),
            lotes=dict(self.lotes),
            movimentacoes=list(self.movimentacoes),
        )

    def saldo_do_lote(self, lote_id: int) -> int:
        return sum(
            (c.quantidade if m.tipo is TipoMovimentacao.ENTRADA else -c.quantidade)
            for m in self.movimentacoes
            for c in m.linhas
            if c.lote_id == lote_id
        )

    def saldo_do_produto(self, produto_id: int) -> int:
        return sum(
            self.saldo_do_lote(lote.id)
            for lote in self.lotes.values()
            if lote.produto_id == produto_id
        )


class RepositorioProdutosEmMemoria:
    def __init__(self, uow: "UnidadeDeTrabalhoEmMemoria") -> None:
        self._uow = uow

    def adicionar(self, nome: NomeValido, categoria: NomeValido | None) -> Produto:
        produtos = self._uow.estado.produtos
        produto = Produto(id=max(produtos, default=0) + 1, nome=nome, categoria=categoria)
        produtos[produto.id] = produto
        return produto

    def buscar_por_nome(self, nome: NomeValido) -> Produto | None:
        return next((p for p in self._uow.estado.produtos.values() if p.nome == nome), None)

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        return self._uow.estado.produtos.get(produto_id)

    def atualizar(self, produto: Produto) -> None:
        self._uow.estado.produtos[produto.id] = produto

    def possui_movimentacoes(self, produto_id: int) -> bool:
        return any(m.produto_id == produto_id for m in self._uow.estado.movimentacoes)

    def remover(self, produto_id: int) -> None:
        del self._uow.estado.produtos[produto_id]

    def listar_resumos(self) -> list[ResumoProduto]:
        estado = self._uow.estado
        ordenados = sorted(estado.produtos.values(), key=lambda p: p.nome.chave)
        return [ResumoProduto.de(p, saldo=estado.saldo_do_produto(p.id)) for p in ordenados]


class RepositorioLotesEmMemoria:
    def __init__(self, uow: "UnidadeDeTrabalhoEmMemoria") -> None:
        self._uow = uow

    def adicionar(
        self, produto_id: int, validade: date | None, fornecedor: NomeValido | None
    ) -> Lote:
        lotes = self._uow.estado.lotes
        lote = Lote(len(lotes) + 1, produto_id, validade, fornecedor)
        lotes[lote.id] = lote
        return lote

    def com_saldo(self, produto_id: int) -> list[LoteComSaldo]:
        estado = self._uow.estado
        lotes = sorted(
            (lote for lote in estado.lotes.values() if lote.produto_id == produto_id),
            key=ordem_fefo,
        )
        com_saldo = (LoteComSaldo(lote, estado.saldo_do_lote(lote.id)) for lote in lotes)
        return [item for item in com_saldo if item.saldo > 0]

    def todos_com_saldo(self) -> list[tuple[str, LoteComSaldo]]:
        estado = self._uow.estado
        return [
            (estado.produtos[item.lote.produto_id].nome.valor, item)
            for produto_id in estado.produtos
            for item in self.com_saldo(produto_id)
        ]

    def resumo_estoque(self) -> list[ItemEstoque]:
        estado = self._uow.estado
        itens = []
        for produto in sorted(estado.produtos.values(), key=lambda p: p.nome.chave):
            lotes = self.com_saldo(produto.id)
            if lotes:
                itens.append(
                    ItemEstoque(
                        produto_id=produto.id,
                        produto=produto.nome.valor,
                        saldo=sum(item.saldo for item in lotes),
                        proxima_validade=lotes[0].lote.validade,
                    )
                )
        return itens


class RepositorioConfiguracaoEmMemoria:
    def __init__(self, uow: "UnidadeDeTrabalhoEmMemoria") -> None:
        self._uow = uow

    def dias_alerta(self) -> int:
        return self._uow.estado.dias_alerta

    def definir_dias_alerta(self, dias: int) -> None:
        self._uow.estado.dias_alerta = dias


class RepositorioMovimentacoesEmMemoria:
    def __init__(self, uow: "UnidadeDeTrabalhoEmMemoria") -> None:
        self._uow = uow

    def registrar(self, movimentacao: Movimentacao) -> int:
        self._uow.estado.movimentacoes.append(movimentacao)
        return len(self._uow.estado.movimentacoes)


class UnidadeDeTrabalhoEmMemoria:
    """Transação simulada: sem `confirmar()`, o estado volta à última confirmação."""

    def __init__(self) -> None:
        self.estado = EstadoEmMemoria()
        self._confirmado = self.estado.copia()
        self.confirmacoes = 0
        self.produtos = RepositorioProdutosEmMemoria(self)
        self.lotes = RepositorioLotesEmMemoria(self)
        self.movimentacoes = RepositorioMovimentacoesEmMemoria(self)
        self.configuracao = RepositorioConfiguracaoEmMemoria(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastro: TracebackType | None,
    ) -> None:
        self.estado = self._confirmado.copia()

    def confirmar(self) -> None:
        self.confirmacoes += 1
        self._confirmado = self.estado.copia()
