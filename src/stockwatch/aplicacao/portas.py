"""Portas (interfaces) que a persistência implementa para a aplicação."""

from types import TracebackType
from typing import Protocol, Self

from stockwatch.aplicacao.dtos import ResumoProduto
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.valores import NomeValido


class RepositorioProdutos(Protocol):
    def adicionar(self, nome: NomeValido, categoria: NomeValido | None) -> Produto: ...

    def buscar_por_nome(self, nome: NomeValido) -> Produto | None: ...

    def listar_resumos(self) -> list[ResumoProduto]:
        """Produtos em ordem alfabética, sem diferenciar maiúsculas, com saldo atual."""
        ...


class UnidadeDeTrabalho(Protocol):
    """Transação de um caso de uso: sem `confirmar()`, tudo é descartado ao sair do bloco."""

    @property
    def produtos(self) -> RepositorioProdutos: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastro: TracebackType | None,
    ) -> None: ...

    def confirmar(self) -> None: ...
