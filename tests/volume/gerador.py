"""Gera um banco do produto com volume de NFR-003 (10 mil produtos, 1 milhão de movimentações).

Os dados são inseridos direto em SQL, numa transação, para a geração levar segundos
e não horas. O resultado é coerente com as regras: cada produto recebe lotes
(entradas) e saídas que os consomem em ordem FEFO, sem saldo negativo.
"""

import random
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from stockwatch.persistencia.sqlite import BancoSqlite

PRODUTOS = 10_000
LOTES_POR_PRODUTO = 40
SAIDAS_POR_PRODUTO = 60  # 40 entradas + 60 saídas = 100 movimentações por produto
UNIDADES_POR_LOTE = 30
UNIDADES_POR_SAIDA = 10  # cada lote atende 3 saídas; 60 saídas esgotam 20 lotes
HOJE = date(2026, 10, 1)
INICIO = datetime(2025, 1, 1, tzinfo=UTC)


def gerar(caminho: Path, semente: int = 20260930) -> None:
    """Cria o banco em `caminho` pelas migrações do produto e o popula."""
    BancoSqlite(caminho).fechar()
    aleatorio = random.Random(semente)
    conexao = sqlite3.connect(caminho, isolation_level=None)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("BEGIN")
    conexao.executemany(
        "INSERT INTO produto (id, nome, nome_chave, criado_em) VALUES (?, ?, ?, ?)",
        (
            (p, f"Produto {p:05d}", f"produto {p:05d}", INICIO.isoformat())
            for p in range(1, PRODUTOS + 1)
        ),
    )
    lotes: list[tuple[int, int, str | None]] = []
    movimentacoes: list[tuple[int, str, str | None, int, str]] = []
    linhas: list[tuple[int, int, int]] = []
    lote_id = movimentacao_id = 0
    instante = INICIO
    for produto in range(1, PRODUTOS + 1):
        validades = sorted(
            (HOJE + timedelta(days=aleatorio.randint(-60, 300)) for _ in range(LOTES_POR_PRODUTO)),
        )
        ids_do_produto = []
        for indice, validade in enumerate(validades):
            lote_id += 1
            movimentacao_id += 1
            instante += timedelta(seconds=1)
            sem_validade = indice == LOTES_POR_PRODUTO - 1  # um lote por produto não vence
            lotes.append((lote_id, produto, None if sem_validade else validade.isoformat()))
            movimentacoes.append((movimentacao_id, "entrada", None, produto, instante.isoformat()))
            linhas.append((movimentacao_id, lote_id, UNIDADES_POR_LOTE))
            ids_do_produto.append(lote_id)
        for saida in range(SAIDAS_POR_PRODUTO):
            movimentacao_id += 1
            instante += timedelta(seconds=1)
            venda = (movimentacao_id, "saida", "venda", produto, instante.isoformat())
            movimentacoes.append(venda)
            linhas.append((movimentacao_id, ids_do_produto[saida // 3], UNIDADES_POR_SAIDA))
    conexao.executemany("INSERT INTO lote (id, produto_id, validade) VALUES (?, ?, ?)", lotes)
    conexao.executemany(
        "INSERT INTO movimentacao (id, tipo, motivo, produto_id, ocorrida_em)"
        " VALUES (?, ?, ?, ?, ?)",
        movimentacoes,
    )
    conexao.executemany(
        "INSERT INTO movimentacao_lote (movimentacao_id, lote_id, quantidade) VALUES (?, ?, ?)",
        linhas,
    )
    conexao.execute("COMMIT")
    conexao.execute("ANALYZE")
    conexao.close()
