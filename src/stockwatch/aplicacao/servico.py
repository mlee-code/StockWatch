"""Casos de uso do estoque."""

from collections.abc import Callable

from stockwatch.aplicacao.dtos import ResumoProduto
from stockwatch.aplicacao.portas import UnidadeDeTrabalho
from stockwatch.dominio.erros import ProdutoDuplicado
from stockwatch.dominio.valores import NomeValido


def _nome_opcional(texto: str | None) -> NomeValido | None:
    return NomeValido(texto) if texto and texto.strip() else None


class ServicoEstoque:
    """Orquestra domínio e persistência; cada método é uma transação."""

    def __init__(self, nova_unidade: Callable[[], UnidadeDeTrabalho]) -> None:
        self._nova_unidade = nova_unidade

    def cadastrar_produto(self, nome: str, categoria: str | None = None) -> ResumoProduto:
        """REQ-001."""
        nome_valido = NomeValido(nome)
        categoria_valida = _nome_opcional(categoria)
        with self._nova_unidade() as uow:
            existente = uow.produtos.buscar_por_nome(nome_valido)
            if existente is not None:
                raise ProdutoDuplicado(f"Já existe um produto chamado “{existente.nome}”.")
            produto = uow.produtos.adicionar(nome_valido, categoria_valida)
            uow.confirmar()
        return ResumoProduto(
            id=produto.id,
            nome=produto.nome.valor,
            categoria=produto.categoria.valor if produto.categoria else None,
            saldo=0,
        )

    def listar_produtos(self) -> list[ResumoProduto]:
        """REQ-002."""
        with self._nova_unidade() as uow:
            return uow.produtos.listar_resumos()
