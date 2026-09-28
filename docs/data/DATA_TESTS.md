# DATA_TESTS.md

Verificações do banco do produto (`DATA_MODEL.md`). Executadas em `tests/integracao/` (SUITE-INT) e `tests/volume/` (SUITE-VOL).

| ID | Verificação | Critério |
|---|---|---|
| DT-001 | Migração | um banco novo chega a `user_version = 1`; reaplicar não muda nada |
| DT-002 | Integridade | `PRAGMA foreign_key_check` vazio e `integrity_check = ok` depois de cada suíte |
| DT-003 | Unicidade | nome de produto, categoria ou fornecedor repetido, com qualquer caixa, é rejeitado |
| DT-004 | Domínios | `tipo`, `motivo`, `quantidade > 0` e a coerência entre tipo e motivo são rejeitados quando inválidos |
| DT-005 | Chaves | um lote ou movimentação com produto inexistente é rejeitado |
| DT-006 | Invariante de saldo | nenhum lote com saldo negativo, verificado por consulta agregada |
| DT-007 | Atomicidade | uma falha no meio de uma saída não deixa linhas parciais |
| DT-008 | Persistência | os dados sobrevivem ao fechamento e à reabertura |
| DT-009 | Navegação | consultas de estoque, validades e histórico retornam o esperado para um cenário conhecido |
| DT-010 | Desempenho | consultas com volume dentro de NFR-003, usando os índices (`EXPLAIN QUERY PLAN` sem varredura completa de `movimentacao_lote`) |
| DT-011 | Privacidade | o banco não guarda dados além dos definidos em `DATA_MODEL.md` |
