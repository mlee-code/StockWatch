# DATA_MODEL.md

## Bancos
| Banco | Finalidade | Local |
|---|---|---|
| Produto | dados funcionais do estoque | `$XDG_DATA_HOME/stockwatch/stockwatch.db` (REQ-010) |
| `metadata` | evidências de engenharia, separadas do produto | `metadata/metadata.sqlite3` (DECISION-002) |

Este documento trata só do banco do produto. A fonte canônica do esquema físico é `src/stockwatch/persistencia/migracoes.py`. O DBML em `workspace/database_design/` é uma projeção.

## Modelo conceitual
- Um **produto** pode ter uma **categoria**.
- Cada **entrada** cria um **lote** com validade e, opcionalmente, um **fornecedor**.
- Uma **movimentação** é uma entrada ou uma saída. Suas **linhas** (`movimentacao_lote`) dizem quantas unidades tocaram cada lote.
- Uma entrada tem exatamente uma linha, no próprio lote. Uma saída tem uma ou mais linhas, conforme o FEFO.

## Entidades

| Tabela | Campo | Tipo | Regras |
|---|---|---|---|
| `categoria` | `id` | INTEGER PK | |
| | `nome` | TEXT | NOT NULL, 1–100 caracteres, como digitado |
| | `nome_chave` | TEXT | NOT NULL, UNIQUE; `nome` em `casefold()` |
| `fornecedor` | `id`, `nome`, `nome_chave` | idem a `categoria` | |
| `produto` | `id` | INTEGER PK | |
| | `nome` | TEXT | NOT NULL, 1–100 caracteres, como digitado |
| | `nome_chave` | TEXT | NOT NULL, UNIQUE; `nome` em `casefold()` |
| | `categoria_id` | INTEGER | FK `categoria`, NULL permitido |
| | `criado_em` | TEXT | ISO 8601 UTC |
| `lote` | `id` | INTEGER PK | ordem de criação; desempate FEFO (H4) |
| | `produto_id` | INTEGER | FK `produto`, NOT NULL |
| | `validade` | TEXT | ISO `AAAA-MM-DD`, NOT NULL, CHECK `validade IS date(validade)` (com `=`, um texto inválido gera NULL e o CHECK passaria) |
| | `fornecedor_id` | INTEGER | FK `fornecedor`, NULL permitido |
| `movimentacao` | `id` | INTEGER PK | |
| | `tipo` | TEXT | CHECK `entrada` ou `saida` |
| | `motivo` | TEXT | NULL em entrada; CHECK `venda`, `perda`, `descarte_vencimento` em saída |
| | `produto_id` | INTEGER | FK `produto`, NOT NULL |
| | `ocorrida_em` | TEXT | ISO 8601 UTC, NOT NULL |
| `movimentacao_lote` | `movimentacao_id` | INTEGER | FK, parte da PK |
| | `lote_id` | INTEGER | FK, parte da PK |
| | `quantidade` | INTEGER | CHECK > 0 |
| `configuracao` | `chave` | TEXT PK | |
| | `valor` | TEXT | NOT NULL; `dias_alerta` = `30` por padrão |

CHECK de coerência: `(tipo = 'entrada' AND motivo IS NULL) OR (tipo = 'saida' AND motivo IS NOT NULL)`.

## Unicidade de nomes
`COLLATE NOCASE` do SQLite só ignora a caixa em letras ASCII: "Éclair" e "éCLAIR" seriam nomes distintos. Por isso a unicidade fica numa coluna `nome_chave`, com a mesma normalização do domínio (`NomeValido.chave`, `str.casefold()`), e o texto original é preservado em `nome`.

## Cardinalidades
- categoria 1 — N produto
- fornecedor 1 — N lote
- produto 1 — N lote
- produto 1 — N movimentacao
- movimentacao N — M lote, via `movimentacao_lote`

## Derivações
Nenhum saldo é armazenado. O saldo é derivado das movimentações.

- **Saldo do lote:** `SUM(CASE tipo WHEN 'entrada' THEN quantidade ELSE -quantidade END)` sobre `movimentacao_lote` JOIN `movimentacao`.
- **Saldo do produto:** soma dos saldos dos seus lotes.
- **Invariante:** o saldo de todo lote é maior ou igual a zero. É garantido pelo serviço (REQ-004 CA-4) e verificado em `DATA_TESTS.md`.

## Índices
- `lote(produto_id, validade, id)`: busca FEFO.
- `movimentacao_lote(lote_id)`: saldo por lote.
- `movimentacao(ocorrida_em)`: histórico.

## Migrações
`PRAGMA user_version` guarda a versão do esquema. Cada migração é aplicada numa transação, e a versão 1 cria o esquema acima.

## Privacidade, criptografia e recuperação
- **Privacidade:** não há dados pessoais além do nome do fornecedor.
- **Criptografia:** sem criptografia adicional.
- **Backup:** cópia do arquivo `.db` com a aplicação fechada. Está documentado no README e fica sem automação na v0.1.0.
