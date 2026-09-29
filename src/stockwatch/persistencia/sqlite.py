"""Adaptadores SQLite das portas da aplicação."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Self

from stockwatch.aplicacao.dtos import ResumoProduto
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.valores import NomeValido
from stockwatch.persistencia.migracoes import migrar

_SALDO_POR_PRODUTO = """
SELECT l.produto_id,
       SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade ELSE -ml.quantidade END) AS saldo
FROM movimentacao_lote ml
JOIN movimentacao m ON m.id = ml.movimentacao_id
JOIN lote l ON l.id = ml.lote_id
GROUP BY l.produto_id
"""


class BancoSqlite:
    """Conexão única do processo (CON-003) e fábrica de unidades de trabalho."""

    def __init__(self, caminho: Path) -> None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        # isolation_level=None: as transações são abertas explicitamente pela unidade.
        self.conexao = sqlite3.connect(caminho, isolation_level=None)
        self.conexao.execute("PRAGMA foreign_keys = ON")
        migrar(self.conexao)

    def nova_unidade(self) -> "UnidadeDeTrabalhoSqlite":
        return UnidadeDeTrabalhoSqlite(self.conexao)

    def fechar(self) -> None:
        self.conexao.close()


class UnidadeDeTrabalhoSqlite:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao
        self.produtos = RepositorioProdutosSqlite(conexao)

    def __enter__(self) -> Self:
        self._conexao.execute("BEGIN")
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastro: TracebackType | None,
    ) -> None:
        if self._conexao.in_transaction:
            self._conexao.execute("ROLLBACK")

    def confirmar(self) -> None:
        self._conexao.execute("COMMIT")


class RepositorioProdutosSqlite:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def adicionar(self, nome: NomeValido, categoria: NomeValido | None) -> Produto:
        categoria_id = self._id_categoria(categoria) if categoria else None
        cursor = self._conexao.execute(
            "INSERT INTO produto (nome, nome_chave, categoria_id, criado_em) VALUES (?, ?, ?, ?)",
            (nome.valor, nome.chave, categoria_id, datetime.now(UTC).isoformat()),
        )
        assert cursor.lastrowid is not None
        return Produto(id=cursor.lastrowid, nome=nome, categoria=categoria)

    def buscar_por_nome(self, nome: NomeValido) -> Produto | None:
        linha = self._conexao.execute(
            """
            SELECT p.id, p.nome, c.nome FROM produto p
            LEFT JOIN categoria c ON c.id = p.categoria_id
            WHERE p.nome_chave = ?
            """,
            (nome.chave,),
        ).fetchone()
        if linha is None:
            return None
        return Produto(
            id=linha[0],
            nome=NomeValido(linha[1]),
            categoria=NomeValido(linha[2]) if linha[2] else None,
        )

    def listar_resumos(self) -> list[ResumoProduto]:
        linhas = self._conexao.execute(
            f"""
            SELECT p.id, p.nome, c.nome, COALESCE(s.saldo, 0)
            FROM produto p
            LEFT JOIN categoria c ON c.id = p.categoria_id
            LEFT JOIN ({_SALDO_POR_PRODUTO}) s ON s.produto_id = p.id
            ORDER BY p.nome_chave
            """
        ).fetchall()
        return [ResumoProduto(id=i, nome=n, categoria=c, saldo=s) for i, n, c, s in linhas]

    def _id_categoria(self, nome: NomeValido) -> int:
        self._conexao.execute(
            "INSERT INTO categoria (nome, nome_chave) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (nome.valor, nome.chave),
        )
        linha = self._conexao.execute(
            "SELECT id FROM categoria WHERE nome_chave = ?", (nome.chave,)
        ).fetchone()
        return int(linha[0])
