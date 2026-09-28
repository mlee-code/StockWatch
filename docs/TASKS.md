# TASKS.md

Tarefas executáveis derivadas de `ROADMAP.md`. Cada tarefa aponta a origem, as fontes e os testes. `[x]` só com os testes verdes.

## V010-02 — Fundação
- [x] TASK-001 — Arquivos de higiene do repositório. Fonte: ENGINEERING_PRACTICES. Teste: presença no commit `fb4ccbc`.
- [x] TASK-002 — Pacote Python, dependências, ruff e mypy. Fonte: ARCHITECTURE "Tecnologias". Teste: `ruff`/`mypy` sem erros.
- [x] TASK-003 — TUI inicial que abre e fecha. Fonte: REQ-009 (parcial), NFR-001. Teste: TEST-TUI-001.
- [x] TASK-004 — CI no GitHub Actions. Fonte: ENGINEERING_PRACTICES "CI/CD". Teste: workflow verde no GitHub (run 36500216951).
- [ ] TASK-005 — Documentação técnica da v0.1.0. Fonte: PROP-001. Teste: revisão humana.
- [x] TASK-006 — Guard rail de arquitetura. Fonte: ARCHITECTURE "Guard rails". Teste: SUITE-ARQ.

## V010-03 — Cadastro e listagem de produtos
- [ ] TASK-010 — Valor `NomeValido` e entidade `Produto`. Fonte: REQ-001 CA-1. Testes: SUITE-UNIT.
- [ ] TASK-011 — Serviço `cadastrar_produto`/`listar_produtos` com repositório em memória. Fonte: REQ-001, 002. Testes: SUITE-UNIT.
- [ ] TASK-012 — Migração v1 e repositório SQLite de produtos. Fonte: DATA_MODEL. Testes: SUITE-INT (DT-001, DT-003).
- [ ] TASK-013 — Tela de produtos. Fonte: REQ-001, 002, UX_UI. Testes: SUITE-TUI.
