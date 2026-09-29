# CONSTRAINTS.md

Todas as restrições estão no estado **aprovado** (origem: `workspace/PROJECT_CONTEXT.md`, `AGENTS.md`).

| ID | Categoria | Restrição | Motivo | Verificação |
|---|---|---|---|---|
| CON-001 | Técnica | Python 3.12+, Textual e SQLite | decisão do responsável | `pyproject.toml` |
| CON-002 | Arquitetura | monolito local; sem servidor, rede, API ou filas | escopo do projeto | revisão; nenhuma dependência de rede |
| CON-003 | Uso | um único usuário, sem acesso concorrente | escopo do projeto | sem locking entre processos |
| CON-004 | Produto | sem IA no produto | `AGENTS.md` | EXEC-001 `deterministic` |
| CON-005 | Custo | somente ferramentas gratuitas e de código aberto | orçamento zero | dependências do `pyproject.toml` |
| CON-006 | Prazo | v0.1.0 em um ciclo, até 2026-09-30 | meta de portfólio | `ROADMAP.md` |
| CON-007 | Plataforma | Linux suportado; outros sistemas não testados | ambiente do responsável | CI em `ubuntu-latest` |
| CON-008 | Dados | toda quantidade em estoque pertence a um lote; a validade do lote é opcional (DECISION-007) | regra de negócio | DT-004, SUITE-PROP |
