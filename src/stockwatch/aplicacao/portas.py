"""Portas (interfaces) que a persistência implementa para a aplicação."""

from datetime import date
from types import TracebackType
from typing import Protocol, Self

from stockwatch.aplicacao.dtos import ItemEstoque, ItemHistorico, ResumoProduto
from stockwatch.dominio.estoque import Lote, LoteComSaldo, Movimentacao
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.valores import NomeValido


class RepositorioProdutos(Protocol):
    def adicionar(self, nome: NomeValido, categoria: NomeValido | None) -> Produto: ...

    def buscar_por_nome(self, nome: NomeValido) -> Produto | None: ...

    def buscar_por_id(self, produto_id: int) -> Produto | None: ...

    def atualizar(self, produto: Produto) -> None: ...

    def possui_movimentacoes(self, produto_id: int) -> bool: ...

    def remover(self, produto_id: int) -> None: ...

    def listar_resumos(self) -> list[ResumoProduto]:
        """Produtos em ordem alfabética, sem diferenciar maiúsculas, com saldo atual."""
        ...

    def contar(self) -> int: ...


class RepositorioLotes(Protocol):
    def adicionar(
        self, produto_id: int, validade: date | None, fornecedor: NomeValido | None
    ) -> Lote: ...

    def com_saldo(self, produto_id: int) -> list[LoteComSaldo]:
        """Lotes do produto com saldo > 0, na ordem de `ordem_fefo`."""
        ...

    def resumo_estoque(self) -> list[ItemEstoque]:
        """Produtos com saldo > 0, em ordem alfabética (REQ-005 CA-1)."""
        ...

    def com_saldo_vencendo_ate(self, limite: date) -> list[tuple[str, LoteComSaldo]]:
        """Lotes com saldo > 0 e validade até `limite`, com o nome do produto.

        Só pré-filtra candidatos a alerta no banco; a classificação continua no domínio.
        """
        ...

    def total_de_unidades(self) -> int: ...


class RepositorioConfiguracao(Protocol):
    def dias_alerta(self) -> int: ...

    def definir_dias_alerta(self, dias: int) -> None: ...


class RepositorioMovimentacoes(Protocol):
    def registrar(self, movimentacao: Movimentacao) -> int: ...

    def recentes(self, limite: int, produto_id: int | None = None) -> list[ItemHistorico]:
        """Da mais recente para a mais antiga; empate pela ordem de registro (REQ-008)."""
        ...


class UnidadeDeTrabalho(Protocol):
    """Transação de um caso de uso: sem `confirmar()`, tudo é descartado ao sair do bloco."""

    @property
    def produtos(self) -> RepositorioProdutos: ...

    @property
    def lotes(self) -> RepositorioLotes: ...

    @property
    def movimentacoes(self) -> RepositorioMovimentacoes: ...

    @property
    def configuracao(self) -> RepositorioConfiguracao: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastro: TracebackType | None,
    ) -> None: ...

    def confirmar(self) -> None: ...
