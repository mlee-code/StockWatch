"""Adaptadores SQLite das portas da aplicação."""

import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from types import TracebackType
from typing import Literal, Self

from stockwatch.aplicacao.dtos import ItemEstoque, ItemHistorico, ResumoProduto
from stockwatch.dominio.estoque import (
    Lote,
    LoteComSaldo,
    MotivoSaida,
    Movimentacao,
    TipoMovimentacao,
)
from stockwatch.dominio.produto import Produto
from stockwatch.dominio.validade import DIAS_ALERTA_PADRAO
from stockwatch.dominio.valores import NomeValido
from stockwatch.persistencia.migracoes import migrar

# Saldo de cada lote, derivado das movimentações (DATA_MODEL.md, "Derivações").
_SALDO_LOTE = """
saldo_lote AS (
    SELECT ml.lote_id,
           SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade ELSE -ml.quantidade END) AS saldo
    FROM movimentacao_lote ml
    JOIN movimentacao m ON m.id = ml.movimentacao_id
    GROUP BY ml.lote_id
)
"""


def _nome_ou_nada(texto: str | None) -> NomeValido | None:
    return NomeValido(texto) if texto else None


def _data_ou_nada(texto: str | None) -> date | None:
    return date.fromisoformat(texto) if texto else None


def _id_por_nome(
    conexao: sqlite3.Connection, tabela: Literal["categoria", "fornecedor"], nome: NomeValido
) -> int:
    """Busca pelo nome normalizado ou cria a linha (categoria e fornecedor são reaproveitados)."""
    conexao.execute(
        f"INSERT INTO {tabela} (nome, nome_chave) VALUES (?, ?) ON CONFLICT DO NOTHING",
        (nome.valor, nome.chave),
    )
    linha = conexao.execute(f"SELECT id FROM {tabela} WHERE nome_chave = ?", (nome.chave,))
    return int(linha.fetchone()[0])


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
        self.lotes = RepositorioLotesSqlite(conexao)
        self.movimentacoes = RepositorioMovimentacoesSqlite(conexao)
        self.configuracao = RepositorioConfiguracaoSqlite(conexao)

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
        categoria_id = _id_por_nome(self._conexao, "categoria", categoria) if categoria else None
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
        return self._produto(linha)

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        linha = self._conexao.execute(
            """
            SELECT p.id, p.nome, c.nome FROM produto p
            LEFT JOIN categoria c ON c.id = p.categoria_id
            WHERE p.id = ?
            """,
            (produto_id,),
        ).fetchone()
        return self._produto(linha)

    def atualizar(self, produto: Produto) -> None:
        categoria = produto.categoria
        categoria_id = _id_por_nome(self._conexao, "categoria", categoria) if categoria else None
        self._conexao.execute(
            "UPDATE produto SET nome = ?, nome_chave = ?, categoria_id = ? WHERE id = ?",
            (produto.nome.valor, produto.nome.chave, categoria_id, produto.id),
        )

    def contar(self) -> int:
        return int(self._conexao.execute("SELECT count(*) FROM produto").fetchone()[0])

    def possui_movimentacoes(self, produto_id: int) -> bool:
        linha = self._conexao.execute(
            "SELECT EXISTS (SELECT 1 FROM movimentacao WHERE produto_id = ?)", (produto_id,)
        ).fetchone()
        return bool(linha[0])

    def remover(self, produto_id: int) -> None:
        # Só produtos sem movimentações chegam aqui (DECISION-010); sem lotes nem linhas
        # dependentes, o id liberado pode ser reutilizado pelo SQLite sem ambiguidade.
        self._conexao.execute("DELETE FROM produto WHERE id = ?", (produto_id,))

    @staticmethod
    def _produto(linha: tuple[int, str, str | None] | None) -> Produto | None:
        if linha is None:
            return None
        return Produto(id=linha[0], nome=NomeValido(linha[1]), categoria=_nome_ou_nada(linha[2]))

    def listar_resumos(self) -> list[ResumoProduto]:
        linhas = self._conexao.execute(
            # O saldo do produto soma as movimentações dele direto (movimentacao.produto_id),
            # sem passar por lote: metade do tempo da versão por lote com 1 milhão de linhas.
            """
            WITH saldo_produto AS (
                SELECT m.produto_id,
                       SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade
                                       ELSE -ml.quantidade END) AS saldo
                FROM movimentacao m
                JOIN movimentacao_lote ml ON ml.movimentacao_id = m.id
                GROUP BY m.produto_id
            )
            SELECT p.id, p.nome, c.nome, COALESCE(s.saldo, 0)
            FROM produto p
            LEFT JOIN categoria c ON c.id = p.categoria_id
            LEFT JOIN saldo_produto s ON s.produto_id = p.id
            ORDER BY p.nome_chave
            """
        ).fetchall()
        return [ResumoProduto(id=i, nome=n, categoria=c, saldo=s) for i, n, c, s in linhas]


class RepositorioLotesSqlite:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def adicionar(
        self, produto_id: int, validade: date | None, fornecedor: NomeValido | None
    ) -> Lote:
        fornecedor_id = (
            _id_por_nome(self._conexao, "fornecedor", fornecedor) if fornecedor else None
        )
        cursor = self._conexao.execute(
            "INSERT INTO lote (produto_id, validade, fornecedor_id) VALUES (?, ?, ?)",
            (produto_id, validade.isoformat() if validade else None, fornecedor_id),
        )
        assert cursor.lastrowid is not None
        return Lote(cursor.lastrowid, produto_id, validade, fornecedor)

    def com_saldo(self, produto_id: int) -> list[LoteComSaldo]:
        linhas = self._conexao.execute(
            """
            SELECT l.id, l.validade, f.nome,
                   (SELECT SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade
                                           ELSE -ml.quantidade END)
                    FROM movimentacao_lote ml
                    JOIN movimentacao m ON m.id = ml.movimentacao_id
                    WHERE ml.lote_id = l.id) AS saldo
            FROM lote l
            LEFT JOIN fornecedor f ON f.id = l.fornecedor_id
            WHERE l.produto_id = ? AND saldo > 0
            ORDER BY l.validade IS NULL, l.validade, l.id
            """,
            (produto_id,),
        ).fetchall()
        return [
            LoteComSaldo(
                Lote(lote_id, produto_id, _data_ou_nada(validade), _nome_ou_nada(fornecedor)),
                saldo,
            )
            for lote_id, validade, fornecedor, saldo in linhas
        ]

    def com_saldo_vencendo_ate(self, limite: date) -> list[tuple[str, LoteComSaldo]]:
        # Filtra primeiro pela validade (índice idx_lote_fefo) e só então calcula o saldo
        # de cada candidato pelo índice de movimentacao_lote: evita agregar o banco inteiro.
        linhas = self._conexao.execute(
            """
            SELECT nome, id, produto_id, validade, fornecedor, saldo FROM (
                SELECT p.nome, l.id, l.produto_id, l.validade, f.nome AS fornecedor,
                       (SELECT SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade
                                               ELSE -ml.quantidade END)
                        FROM movimentacao_lote ml
                        JOIN movimentacao m ON m.id = ml.movimentacao_id
                        WHERE ml.lote_id = l.id) AS saldo
                FROM lote l
                JOIN produto p ON p.id = l.produto_id
                LEFT JOIN fornecedor f ON f.id = l.fornecedor_id
                WHERE l.validade IS NOT NULL AND l.validade <= ?
            )
            WHERE saldo > 0
            ORDER BY validade, id
            """,
            (limite.isoformat(),),
        ).fetchall()
        return [
            (
                produto,
                LoteComSaldo(
                    Lote(lote_id, produto_id, _data_ou_nada(validade), _nome_ou_nada(fornecedor)),
                    saldo,
                ),
            )
            for produto, lote_id, produto_id, validade, fornecedor, saldo in linhas
        ]

    def total_de_unidades(self) -> int:
        linha = self._conexao.execute(
            """
            SELECT COALESCE(SUM(CASE m.tipo WHEN 'entrada' THEN ml.quantidade
                                            ELSE -ml.quantidade END), 0)
            FROM movimentacao_lote ml JOIN movimentacao m ON m.id = ml.movimentacao_id
            """
        ).fetchone()
        return int(linha[0])

    def resumo_estoque(self) -> list[ItemEstoque]:
        linhas = self._conexao.execute(
            f"""
            WITH {_SALDO_LOTE}
            SELECT p.id, p.nome, SUM(s.saldo), MIN(l.validade)
            FROM saldo_lote s
            JOIN lote l ON l.id = s.lote_id
            JOIN produto p ON p.id = l.produto_id
            WHERE s.saldo > 0
            GROUP BY p.id
            ORDER BY p.nome_chave
            """
        ).fetchall()
        return [
            ItemEstoque(produto_id=i, produto=n, saldo=s, proxima_validade=_data_ou_nada(v))
            for i, n, s, v in linhas
        ]


class RepositorioMovimentacoesSqlite:
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def registrar(self, movimentacao: Movimentacao) -> int:
        cursor = self._conexao.execute(
            "INSERT INTO movimentacao (tipo, motivo, produto_id, ocorrida_em) VALUES (?, ?, ?, ?)",
            (
                movimentacao.tipo.value,
                movimentacao.motivo.value if movimentacao.motivo else None,
                movimentacao.produto_id,
                movimentacao.ocorrida_em.astimezone(UTC).isoformat(),
            ),
        )
        assert cursor.lastrowid is not None
        self._conexao.executemany(
            "INSERT INTO movimentacao_lote (movimentacao_id, lote_id, quantidade) VALUES (?, ?, ?)",
            [(cursor.lastrowid, c.lote_id, c.quantidade) for c in movimentacao.linhas],
        )
        return cursor.lastrowid

    def recentes(self, limite: int, produto_id: int | None = None) -> list[ItemHistorico]:
        # O índice em ocorrida_em atende ao ORDER BY ... LIMIT sem ordenar a tabela inteira.
        linhas = self._conexao.execute(
            """
            SELECT m.id, m.ocorrida_em, m.tipo, m.motivo, p.nome,
                   (SELECT SUM(quantidade) FROM movimentacao_lote WHERE movimentacao_id = m.id)
            FROM movimentacao m
            JOIN produto p ON p.id = m.produto_id
            WHERE :produto IS NULL OR m.produto_id = :produto
            ORDER BY m.ocorrida_em DESC, m.id DESC
            LIMIT :limite
            """,
            {"produto": produto_id, "limite": limite},
        ).fetchall()
        return [
            ItemHistorico(
                mov_id,
                datetime.fromisoformat(ocorrida_em),
                TipoMovimentacao(tipo),
                MotivoSaida(motivo) if motivo else None,
                produto,
                quantidade,
            )
            for mov_id, ocorrida_em, tipo, motivo, produto, quantidade in linhas
        ]


class RepositorioConfiguracaoSqlite:
    """Tabela chave-valor `configuracao`; `dias_alerta` nasce com 30 na migração 1."""

    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def dias_alerta(self) -> int:
        linha = self._conexao.execute(
            "SELECT valor FROM configuracao WHERE chave = 'dias_alerta'"
        ).fetchone()
        return int(linha[0]) if linha else DIAS_ALERTA_PADRAO

    def definir_dias_alerta(self, dias: int) -> None:
        self._conexao.execute(
            """
            INSERT INTO configuracao (chave, valor) VALUES ('dias_alerta', ?)
            ON CONFLICT (chave) DO UPDATE SET valor = excluded.valor
            """,
            (str(dias),),
        )
