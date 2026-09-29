"""Dublês em memória das portas da aplicação, para testes que não avaliam integração."""

from types import TracebackType
from typing import Self

from stockwatch.aplicacao.dtos import ResumoProduto
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.valores import NomeValido


class RepositorioProdutosEmMemoria:
    def __init__(self) -> None:
        self._produtos: dict[int, Produto] = {}

    def adicionar(self, nome: NomeValido, categoria: NomeValido | None) -> Produto:
        produto = Produto(id=len(self._produtos) + 1, nome=nome, categoria=categoria)
        self._produtos[produto.id] = produto
        return produto

    def buscar_por_nome(self, nome: NomeValido) -> Produto | None:
        return next((p for p in self._produtos.values() if p.nome == nome), None)

    def listar_resumos(self) -> list[ResumoProduto]:
        ordenados = sorted(self._produtos.values(), key=lambda p: p.nome.chave)
        return [ResumoProduto.de(p, saldo=0) for p in ordenados]


class UnidadeDeTrabalhoEmMemoria:
    """Confirma ou descarta alterações como uma transação, guardando uma cópia."""

    def __init__(self) -> None:
        self.produtos = RepositorioProdutosEmMemoria()
        self.confirmacoes = 0
        self._copia: dict[int, Produto] = {}

    def __enter__(self) -> Self:
        self._copia = dict(self.produtos._produtos)
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastro: TracebackType | None,
    ) -> None:
        # Sem confirmação, tudo o que foi feito dentro do bloco é descartado.
        self.produtos._produtos = self._copia

    def confirmar(self) -> None:
        self.confirmacoes += 1
        self._copia = dict(self.produtos._produtos)
