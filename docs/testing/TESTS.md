# TESTS.md

## Objetivo
Transformar `REQUIREMENTS.md` em verificações executáveis, construídas por TDD canônico (Red → Green → Refactor → Regression), da regra pura até a jornada completa na TUI.

## Princípios
- Os critérios de aceitação ficam em `REQUIREMENTS.md`; cada teste cita o `REQ`/`CA` que verifica, na docstring.
- Todo teste novo falha pelo motivo correto antes da implementação; o commit `test:` registra o Red, e o `feat:` registra o Green.
- Nenhum teste é enfraquecido, ignorado ou removido para avançar.
- Testes que não verificam integração usam repositórios em memória e relógio fixo.

## Como executar
```sh
.venv/bin/pytest                    # padrão: tudo menos volume
.venv/bin/pytest -m volume          # volume (lento)
.venv/bin/pytest tests/desempenho --benchmark-only
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
```
O CI (`.github/workflows/ci.yml`) roda o conjunto padrão a cada push.

## Tipos de teste e critérios de aceitação

### SUITE-UNIT — Unitários (`tests/unit/`)
- **Objeto:** entidades, valores, regras puras e serviço com repositórios em memória.
- **Critério:** todos os CA de REQ-001 a REQ-009 com pelo menos um caso de sucesso, um de erro e os limites (por exemplo, nome com 0, 1, 100 e 101 caracteres; N = 0 e 365). Cobertura de linhas do domínio ≥ 95%.

### SUITE-PROP — Baseados em propriedades (`tests/propriedades/`)
- **Objeto:** `planejar_saida` (FEFO) e `classificar` (validade).
- **Critério:** Hypothesis com pelo menos 500 exemplos por propriedade, sem falha. Propriedades obrigatórias:
  - a soma consumida é igual à pedida, ou a saída é rejeitada;
  - nenhum lote fica com saldo negativo;
  - um lote só é consumido depois que todos os lotes elegíveis de validade anterior se esgotaram;
  - venda nunca toca lote vencido; descarte nunca toca lote válido;
  - a classificação é consistente com a definição de H5 para qualquer data e N.

### SUITE-INT — Integração com SQLite real (`tests/integracao/`)
- **Objeto:** repositórios, migrações, unidade de trabalho.
- **Critério:**
  - banco em arquivo temporário real, não `:memory:`;
  - cada restrição de `DATA_MODEL.md` rejeita um dado inválido;
  - rollback deixa o banco idêntico ao anterior;
  - os dados sobrevivem ao fechamento e à reabertura (REQ-010).

### SUITE-TUI — Interface (`tests/tui/`)
- **Objeto:** telas via `App.run_test()` e piloto de teclado.
- **Critério:** cada tela cobre os estados vazio, erro e sucesso (NFR-002), e cada fluxo é executado só pelo teclado (NFR-001).

### SUITE-FUZZ — Fuzzing (`tests/fuzzing/`)
- **Objeto:** analisadores de entrada (quantidade, data, nome) e o serviço completo.
- **Critério:**
  - texto arbitrário nos analisadores gera um valor válido ou `ErroDominio`, nunca outra exceção;
  - a máquina de estados do Hypothesis (sequências aleatórias de cadastrar, entrar, sair e avançar a data) mantém todas as invariantes;
  - pelo menos 200 sequências de até 50 passos, sem falha.

### SUITE-VOL — Volume (`tests/volume/`, marcador `volume`)
- **Objeto:** banco com 10 mil produtos e 1 milhão de movimentações.
- **Critério:** as metas de NFR-003 atendidas, e o invariante de saldo verificado por consulta sobre o banco inteiro.

### SUITE-DES — Desempenho e profiling (`tests/desempenho/`)
- **Objeto:** operações de NFR-003 com pytest-benchmark; cProfile e tracemalloc nos mesmos cenários.
- **Critério:** as métricas são registradas em `metadata` com o ambiente e a baseline (DECISION-003). Uma regressão acima de 20% no p95 contra a baseline no mesmo ambiente reprova o portão.

### SUITE-ARQ — Arquitetura (`tests/arquitetura/`)
- **Critério:** as regras de dependência de `ARCHITECTURE.md` ("Guard rails arquiteturais") são respeitadas.

## Casos
Cada arquivo de teste identifica seus casos como `TEST-<SUITE>-NNN` na docstring. Os casos implementados:

| ID | Verifica | Arquivo |
|---|---|---|
| TEST-TUI-001, 002 | a aplicação abre, fecha com `q` e usa o tema neutro | `tests/tui/test_app.py` |
| TEST-TUI-003 a 008 | tela de produtos: vazio, cadastro por teclado, erros, Esc | `tests/tui/test_tela_produtos.py` |
| TEST-UNIT-001 a 006 | `NomeValido` (REQ-001 CA-1, H6) | `tests/unit/test_nome_valido.py` |
| TEST-UNIT-010 a 016 | cadastro e listagem no serviço (REQ-001, 002) | `tests/unit/test_servico_produtos.py` |
| TEST-UNIT-020 a 022 | local do banco (REQ-010 CA-3) | `tests/unit/test_main.py` |
| TEST-INT-001 a 010 | migração, transações, unicidade e persistência de produtos | `tests/integracao/test_produtos_sqlite.py` |
| TEST-INT-011 | fluxo TUI → SQLite com reinício | `tests/integracao/test_fluxo_produtos.py` |
| TEST-INT-012 | rollback de migração com erro | `tests/integracao/test_migracoes.py` |
| TEST-ARQ-001, 002 | camadas e dependências | `tests/arquitetura/test_dependencias.py` |

## Portões por parte
Cada parte do roadmap só termina com: suíte padrão verde, ruff e mypy sem erros, e os tipos de teste que a parte exige presentes.
