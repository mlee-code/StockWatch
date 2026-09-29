"""Casos de uso do estoque."""

from collections.abc import Callable
from datetime import UTC, date, datetime

from stockwatch.aplicacao.dtos import ItemEstoque, ResumoEntrada, ResumoProduto, SaldoLote
from stockwatch.aplicacao.portas import UnidadeDeTrabalho
from stockwatch.dominio.erros import ProdutoDuplicado, ProdutoInexistente
from stockwatch.dominio.estoque import Movimentacao
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.valores import NomeValido


def _nome_opcional(texto: str | None) -> NomeValido | None:
    return NomeValido(texto) if texto and texto.strip() else None


def _agora_utc() -> datetime:
    return datetime.now(UTC)


class ServicoEstoque:
    """Orquestra domínio e persistência; cada método é uma transação."""

    def __init__(
        self,
        nova_unidade: Callable[[], UnidadeDeTrabalho],
        agora: Callable[[], datetime] = _agora_utc,
    ) -> None:
        self._nova_unidade = nova_unidade
        self._agora = agora

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
        return ResumoProduto.de(produto, saldo=0)

    def listar_produtos(self) -> list[ResumoProduto]:
        """REQ-002."""
        with self._nova_unidade() as uow:
            return uow.produtos.listar_resumos()

    def registrar_entrada(
        self,
        produto: str,
        quantidade: int,
        validade: date | None,
        fornecedor: str | None = None,
    ) -> ResumoEntrada:
        """REQ-003: cria um lote e a movimentação de entrada que o abastece."""
        nome = NomeValido(produto)
        fornecedor_valido = _nome_opcional(fornecedor)
        with self._nova_unidade() as uow:
            encontrado = self._produto_existente(uow, nome)
            lote = uow.lotes.adicionar(encontrado.id, validade, fornecedor_valido)
            uow.movimentacoes.registrar(
                Movimentacao.entrada(
                    produto_id=encontrado.id,
                    lote_id=lote.id,
                    quantidade=quantidade,
                    ocorrida_em=self._agora(),
                )
            )
            saldo = sum(item.saldo for item in uow.lotes.com_saldo(encontrado.id))
            uow.confirmar()
        return ResumoEntrada(encontrado.nome.valor, lote.id, quantidade, validade, saldo)

    def estoque_atual(self) -> list[ItemEstoque]:
        """REQ-005 CA-1."""
        with self._nova_unidade() as uow:
            return uow.lotes.resumo_estoque()

    def lotes_do_produto(self, produto_id: int) -> list[SaldoLote]:
        """REQ-005 CA-2."""
        with self._nova_unidade() as uow:
            return [SaldoLote.de(item) for item in uow.lotes.com_saldo(produto_id)]

    @staticmethod
    def _produto_existente(uow: UnidadeDeTrabalho, nome: NomeValido) -> Produto:
        encontrado = uow.produtos.buscar_por_nome(nome)
        if encontrado is None:
            raise ProdutoInexistente(f"Não há produto chamado “{nome}”.")
        return encontrado
