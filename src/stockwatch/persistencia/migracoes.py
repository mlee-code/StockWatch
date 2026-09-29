"""Esquema do banco do produto; fonte canônica do esquema físico (DATA_MODEL.md).

Cada item de MIGRACOES leva o banco da versão i para i + 1, controlada por
`PRAGMA user_version`. Migrações publicadas nunca são alteradas; mudanças
entram como uma nova migração no fim da lista.
"""

import sqlite3

_V1 = """
CREATE TABLE categoria (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(nome) BETWEEN 1 AND 100),
    nome_chave TEXT NOT NULL UNIQUE
);

CREATE TABLE fornecedor (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(nome) BETWEEN 1 AND 100),
    nome_chave TEXT NOT NULL UNIQUE
);

CREATE TABLE produto (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(nome) BETWEEN 1 AND 100),
    nome_chave TEXT NOT NULL UNIQUE,
    categoria_id INTEGER REFERENCES categoria(id),
    criado_em TEXT NOT NULL
);

CREATE TABLE lote (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produto(id),
    validade TEXT NOT NULL CHECK (validade = date(validade)),
    fornecedor_id INTEGER REFERENCES fornecedor(id)
);
CREATE INDEX idx_lote_fefo ON lote(produto_id, validade, id);

CREATE TABLE movimentacao (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    motivo TEXT CHECK (motivo IN ('venda', 'perda', 'descarte_vencimento')),
    produto_id INTEGER NOT NULL REFERENCES produto(id),
    ocorrida_em TEXT NOT NULL,
    CHECK ((tipo = 'entrada' AND motivo IS NULL) OR (tipo = 'saida' AND motivo IS NOT NULL))
);
CREATE INDEX idx_movimentacao_ocorrida_em ON movimentacao(ocorrida_em);

CREATE TABLE movimentacao_lote (
    movimentacao_id INTEGER NOT NULL REFERENCES movimentacao(id),
    lote_id INTEGER NOT NULL REFERENCES lote(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    PRIMARY KEY (movimentacao_id, lote_id)
);
CREATE INDEX idx_movimentacao_lote_lote ON movimentacao_lote(lote_id);

CREATE TABLE configuracao (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
INSERT INTO configuracao (chave, valor) VALUES ('dias_alerta', '30');
"""

MIGRACOES: tuple[str, ...] = (_V1,)


def migrar(conexao: sqlite3.Connection, migracoes: tuple[str, ...] = MIGRACOES) -> None:
    """Aplica, cada uma em sua transação, as migrações pendentes."""
    versao: int = conexao.execute("PRAGMA user_version").fetchone()[0]
    for numero, script in enumerate(migracoes[versao:], start=versao + 1):
        conexao.execute("BEGIN")
        try:
            for comando in _comandos(script):
                conexao.execute(comando)
            conexao.execute(f"PRAGMA user_version = {numero}")
            conexao.execute("COMMIT")
        except BaseException:
            conexao.execute("ROLLBACK")
            raise


def _comandos(script: str) -> list[str]:
    """Separa o script em comandos; executescript() faria COMMIT implícito."""
    return [c.strip() for c in script.split(";") if c.strip()]
