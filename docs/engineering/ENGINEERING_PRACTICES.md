<!-- Fonte oficial das práticas técnicas transversais adotadas pelo projeto; deve ser adaptada, versionada e ligada a critérios verificáveis. -->

# ENGINEERING_PRACTICES.md

## Escopo
Python 3.12, Textual e SQLite; um monolito local de usuário único (EXEC-001). Não há rede nem serviço implantado.

## Vocabulário normativo
- DEVE / NÃO DEVE: obrigação ou proibição verificável.
- DEVERIA: prática preferencial; desvio exige justificativa.
- PODE: opção permitida.

## Existência e unicidade
- Regras de negócio DEVEM existir uma única vez, no domínio. A TUI não repete validações de regra; ela só converte texto em valores.
- Valores derivados (saldo, classificação de validade) NÃO DEVEM ser armazenados (`DATA_MODEL.md`).

## Design e implementação
- **Dependências:** direção e limites em `ARCHITECTURE.md`, verificados por SUITE-ARQ.
- **Domínio sem efeitos:** o domínio NÃO DEVE fazer I/O, ler o relógio ou acessar o banco. Data de hoje e persistência são injetadas.
- **Imutabilidade:** entidades e valores DEVERIAM ser `dataclass(frozen=True, slots=True)`.
- **Erros:** regras violadas DEVEM lançar subclasses de `ErroDominio`. A TUI DEVE mostrá-las como mensagem, sem traceback.
- **Concorrência:** não há; uso único (CON-003).
- **Automação:**
  - `scripts/verificar.sh` roda lint, formatação, tipos e testes, parando no primeiro erro. É o portão local antes de todo commit `feat:`/`refactor:`/`fix:`. Não é um hook de pré-commit, porque o commit `test:` do TDD registra de propósito um teste vermelho;
  - `ruff check`, `ruff format --check` e `mypy` estrito DEVEM passar antes de cada commit;
  - o CI repete essas verificações a cada push.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/), com descrição em português. O TDD aparece no histórico: `test:` (Red) → `feat:` (Green) → `refactor:`.
- **Nomes:** em português, sem acentos, seguindo a PEP 8 (DECISION-001).
- **Higiene:** `.gitignore`, `.editorconfig` e `.gitattributes` presentes.

## Dados
Ver `docs/data/DATA_MODEL.md` e `DATA_TESTS.md`. O SQL DEVE ser sempre parametrizado, e `PRAGMA foreign_keys = ON` DEVE valer em toda conexão.

## Qualidade, segurança, acessibilidade e operação
- **Testes:** estratégia e portões em `docs/testing/TESTS.md`.
- **Segurança:** SQL parametrizado; sem rede, sem segredos e sem execução de entrada do usuário.
- **Acessibilidade:** operação completa por teclado (NFR-001).
- **Desempenho:** baseline e limites em NFR-003 e DECISION-003.
- **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`). Sem CD: a distribuição é por `pipx` a partir do repositório.

## Referências avaliadas

### PRACTICE-REF-001 — Testes de apps Textual
- Entidade responsável: Textualize
- URI oficial: https://textual.textualize.io/guide/testing/
- Versão: Textual 8.2.8
- Consultada em: 2026-09-28
- Escopo aplicável: SUITE-TUI
- Critério derivado: `App.run_test()` com `Pilot` para teclado; pytest-asyncio no modo `auto`
- Teste ou portão: `tests/tui/`

### PRACTICE-REF-002 — Hypothesis
- Entidade responsável: projeto Hypothesis
- URI oficial: https://hypothesis.readthedocs.io/
- Versão: 6.168
- Consultada em: 2026-09-28
- Escopo aplicável: SUITE-PROP e SUITE-FUZZ
- Critério derivado: `@given` para propriedades; `RuleBasedStateMachine` para sequências
- Teste ou portão: `tests/propriedades/`, `tests/fuzzing/`

## Desvios aprovados

### PRACTICE-DEV-001 — Containerização
- Decisão relacionada: DECISION-006
- Razão: TUI local de usuário único, sem serviço implantado; um container não agrega isolamento útil e complica o uso do terminal.
- Risco: nenhum relevante.
- Controle compensatório: instalação reproduzível por `pipx` e CI em ambiente limpo.
- Prazo de revisão: se surgir execução em servidor.

### PRACTICE-DEV-002 — Testes de mutação
- Decisão relacionada: DECISION-006
- Razão: prazo de dois dias. A bateria de propriedades e fuzzing cobre o risco principal (regras FEFO e validade).
- Risco: testes fracos não detectados.
- Controle compensatório: propriedades com invariantes explícitas e revisão dos testes.
- Prazo de revisão: ciclo seguinte à v0.1.0.
