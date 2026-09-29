# TASKS.md

Tarefas executáveis derivadas de `ROADMAP.md`. Cada tarefa aponta a origem, as fontes e os testes. `[x]` só com os testes verdes.

## V010-02 — Fundação
- [x] TASK-001 — Arquivos de higiene do repositório. Fonte: ENGINEERING_PRACTICES. Teste: presença no commit `fb4ccbc`.
- [x] TASK-002 — Pacote Python, dependências, ruff e mypy. Fonte: ARCHITECTURE "Tecnologias". Teste: `ruff`/`mypy` sem erros.
- [x] TASK-003 — TUI inicial que abre e fecha. Fonte: REQ-009 (parcial), NFR-001. Teste: TEST-TUI-001.
- [x] TASK-004 — CI no GitHub Actions. Fonte: ENGINEERING_PRACTICES "CI/CD". Teste: workflow verde no GitHub (run 36500216951).
- [x] TASK-005 — Documentação técnica da v0.1.0. Fonte: PROP-001. Teste: revisão humana.
- [x] TASK-006 — Guard rail de arquitetura. Fonte: ARCHITECTURE "Guard rails". Teste: SUITE-ARQ.

## V010-03 — Cadastro e listagem de produtos
- [x] TASK-010 — Valor `NomeValido` e entidade `Produto`. Fonte: REQ-001 CA-1. Testes: SUITE-UNIT.
- [x] TASK-011 — Serviço `cadastrar_produto`/`listar_produtos` com repositório em memória. Fonte: REQ-001, 002. Testes: SUITE-UNIT.
- [x] TASK-012 — Migração v1 e repositório SQLite de produtos. Fonte: DATA_MODEL. Testes: SUITE-INT (DT-001, DT-003).
- [x] TASK-013 — Tela de produtos. Fonte: REQ-001, 002, UX_UI. Testes: SUITE-TUI.

## V010-04 — Entrada com lote e validade + estoque atual
- [x] TASK-020 — Leitura de quantidade e data digitadas. Fonte: REQ-003 CA-1, CA-2. Testes: TEST-UNIT-030 a 033.
- [x] TASK-021 — Lote, Consumo e Movimentacao com invariantes. Fonte: CON-008, DATA_MODEL. Testes: TEST-UNIT-050 a 056.
- [x] TASK-022 — Serviço `registrar_entrada`, `estoque_atual`, `lotes_do_produto`. Fonte: REQ-003, 005. Testes: TEST-UNIT-040 a 048.
- [x] TASK-023 — Repositórios SQLite de lotes e movimentações. Fonte: DATA_MODEL. Testes: TEST-INT-020 a 025.
- [x] TASK-024 — Telas de entrada e de estoque. Fonte: REQ-003, 005, UX_UI. Testes: TEST-TUI-010 a 022.
